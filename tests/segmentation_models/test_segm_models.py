import torch
import pytest
import numpy as np
import pytorch_tools as pt
import pytorch_tools.segmentation_models as pt_sm


INP = torch.ones(2, 3, 64, 64)
ENCODERS = ["resnet34", "se_resnet50", "efficientnet_b1", "densenet121"]


def _test_forward(model):
    with torch.no_grad():
        return model(INP)


@pytest.mark.parametrize("encoder_name", ENCODERS)
@pytest.mark.parametrize("model_class", [pt_sm.Unet, pt_sm.Linknet, pt_sm.DeepLabV3])
def test_forward(encoder_name, model_class):
    m = model_class(encoder_name=encoder_name)
    _test_forward(m)


@pytest.mark.parametrize("encoder_name", ENCODERS)
@pytest.mark.parametrize("model_class", [pt_sm.Unet, pt_sm.Linknet, pt_sm.DeepLabV3])
def test_inplace_abn(encoder_name, model_class):
    """check than passing `inplaceabn` really changes all norm activations"""
    m = model_class(encoder_name=encoder_name, norm_layer="inplaceabn", norm_act="leaky_relu")
    _test_forward(m)

    def check_bn(module):
        assert not isinstance(module, pt.modules.ABN)
        for child in module.children():
            check_bn(child)

    check_bn(m)


@pytest.mark.parametrize("encoder_name", ENCODERS)
@pytest.mark.parametrize("model_class", [pt_sm.Unet, pt_sm.Linknet, pt_sm.DeepLabV3])
def test_num_classes(encoder_name, model_class):
    m = model_class(encoder_name=encoder_name, num_classes=5)
    _test_forward(m)


@pytest.mark.parametrize("encoder_name", ENCODERS)
@pytest.mark.parametrize("model_class", [pt_sm.DeepLabV3])  # pt_sm.Unet, pt_sm.Linknet
@pytest.mark.parametrize("output_stride", [32, 16, 8])
def test_dilation(encoder_name, model_class, output_stride):
    m = model_class(encoder_name=encoder_name, output_stride=output_stride)
    _test_forward(m)


@pytest.mark.parametrize("output_stride", [16, 8])
def test_deeplab_last_upsample(output_stride):
    m = pt_sm.DeepLabV3(last_upsample=True, output_stride=output_stride)
    out = _test_forward(m)
    assert out.shape[-2:] == INP.shape[-2:]

    m = pt_sm.DeepLabV3(last_upsample=False, output_stride=output_stride)
    out = _test_forward(m)
    W, H = INP.shape[-2:]
    # should be 4 times smaller
    assert tuple(out.shape[-2:]) == (W // 4, H // 4)
