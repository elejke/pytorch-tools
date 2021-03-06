import pytorch_tools.models as models

ENCODER_SHAPES = {
    "vgg11_bn": (512, 512, 512, 256, 128),
    "vgg13_bn": (512, 512, 512, 256, 128),
    "vgg16_bn": (512, 512, 512, 256, 128),
    "vgg19_bn": (512, 512, 512, 256, 128),
    "resnet18": (512, 256, 128, 64, 64),
    "resnet34": (512, 256, 128, 64, 64),
    "resnet50": (2048, 1024, 512, 256, 64),
    "resnet101": (2048, 1024, 512, 256, 64),
    "resnet152": (2048, 1024, 512, 256, 64),
    "se_resnet34": (512, 256, 128, 64, 64),
    "se_resnet50": (2048, 1024, 512, 256, 64),
    "se_resnet101": (2048, 1024, 512, 256, 64),
    "se_resnet152": (2048, 1024, 512, 256, 64),
    "se_resnext50_32x4d": (2048, 1024, 512, 256, 64),
    "se_resnext101_32x4d": (2048, 1024, 512, 256, 64),
    "densenet121": (1024, 1024, 512, 256, 64),
    "densenet169": (1664, 1280, 512, 256, 64),
    "densenet201": (1920, 1792, 512, 256, 64),
    #'densenet161': (2208, 2112, 768, 384, 96),
    "efficientnet_b0": (1280, 80, 40, 24, 16),
    "efficientnet_b1": (1280, 80, 40, 24, 16),
    "efficientnet_b2": (1408, 88, 48, 24, 16),
    "efficientnet_b3": (1536, 96, 48, 32, 24),
    "efficientnet_b4": (1792, 112, 56, 32, 24),
    "efficientnet_b5": (2048, 128, 64, 40, 24),
    "efficientnet_b6": (2304, 144, 72, 40, 32),
    "efficientnet_b7": (2560, 160, 80, 48, 32),
}


def get_encoder(name, **kwargs):
    if name not in models.__dict__:
        raise ValueError(f"No such encoder: {name}")
    kwargs["encoder"] = True
    # if 'resne' in name:
    #    kwargs['dilated'] = True # dilate resnets for better performance
    kwargs["pretrained"] = kwargs.pop("encoder_weights")
    m = models.__dict__[name](**kwargs)
    m.out_shapes = ENCODER_SHAPES[name]
    return m
