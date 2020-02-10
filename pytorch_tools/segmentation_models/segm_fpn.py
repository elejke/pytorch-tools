import torch
import torch.nn as nn
from pytorch_tools.modules.fpn import FPN
from pytorch_tools.modules import bn_from_name
from pytorch_tools.modules.residual import conv1x1
from pytorch_tools.modules.residual import conv3x3
from pytorch_tools.modules.decoder import SegmentationUpsample
from pytorch_tools.utils.misc import initialize
from .encoders import get_encoder


class PanopticDecoder(nn.Module):
    """ Takes a feature pyramid, upscales the feature map to the same size and merges by sum or concatenation"""
    def __init__(self, 
        pyramid_channels=256,
        segmentation_channels=128,
        merge_policy="add",
        **bn_args,
    ):
 
        super().__init__()
        self.seg_blocks = nn.ModuleList([
            SegmentationUpsample(pyramid_channels, segmentation_channels, n_upsamples=n_upsamples, **bn_args)
            for n_upsamples in [3, 2, 1, 0]
        ])
        self.policy = merge_policy
        initialize(self)


    def forward(self, features):
        c5, c4, c3, c2, c1 = features
        feature_pyramid = [seg_block(p) for seg_block, p in zip(self.seg_blocks, [c5, c4, c3, c2])]
        if self.policy == "add":
            return sum(feature_pyramid)
        elif self.policy == "cat":
            return torch.cat(feature_pyramid, dim=1)
        else:
            raise ValueError("Merge policy must be in {`add`, `cat`}")


class SegmentationFPN(nn.Module):
    """This model uses features generated by FPN and merges them into final prediction
    Ref https://arxiv.org/pdf/1901.02446.pdf

    Args:
        encoder_name (str): name of classification model (without last dense layers) used as feature
            extractor to build segmentation model.
        encoder_weights (str): one of ``None`` (random initialization), ``imagenet`` (pre-training on ImageNet).
        pyramid_channels (int): Feature pyramid output channels. Defaults to 256.
        segmentation_channels (int): Number of segmentation output channels. Defaults to 128.
        num_classes (int): a number of classes for output (output shape - ``(batch, classes, h, w)``).
        merge_policy (str): One of `add` of `cat`. `sum` would sum resulting feature maps.
            `cat` would concatenate them. Defaults to "add".
        last_upsample (bool): Flag to enable upsampling predictions to the original image size. If set to `False` prediction
            would be 4x times smaller than input image. Default True.
        norm_layer (str): Normalization layer to use. One of 'abn', 'inplaceabn'. The inplace version lowers memory
            footprint. But increases backward time. Defaults to 'abn'.
        norm_act (str): Activation for normalizion layer. 'inplaceabn' doesn't support `ReLU` activation.
    
    """

    def __init__(
        self,
        encoder_name="resnet34",
        encoder_weights="imagenet",
        pyramid_channels=256, 
        segmentation_channels=128,
        num_classes=1,
        merge_policy="add",
        last_upsample=True,
        norm_layer="abn",
        norm_act="relu",
        **encoder_params,
    ):  
        super().__init__()
        self.encoder = get_encoder(
            encoder_name,
            norm_layer=norm_layer,
            norm_act=norm_act,
            encoder_weights=encoder_weights,
            **encoder_params,
        )

        self.fpn = FPN(self.encoder.out_shapes, pyramid_channels=pyramid_channels)

        self.decoder = PanopticDecoder(
            pyramid_channels=pyramid_channels,
            segmentation_channels=segmentation_channels,
            merge_policy=merge_policy,
            norm_layer=bn_from_name(norm_layer),
            norm_act=norm_act,
        )
        if merge_policy == "cat":
            segmentation_channels *= 4
        self.segm_head = conv1x1(segmentation_channels, num_classes)
        self.upsample = nn.Upsample(scale_factor=4, mode="bilinear") if last_upsample else nn.Identity()
        self.name = f"segm-fpn-{encoder_name}"

    def forward(self, x):
        x = self.encoder(x) # return 5 features maps
        x = self.fpn(x) # returns 5 features maps
        x = self.decoder(x) # return 1 feature map
        x = self.segm_head(x)
        x = self.upsample(x)
        return x