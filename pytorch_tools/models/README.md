# Just Another PyTorch Model Zoo
All models here were either written from scratch or refactored from open-source implementations.  
All models here use `Activated Normalization` layers instead of traditional `Normalization` followed by `Activation`. It makes changing activation function and normalization layer easy and convenient. It also allows using [Inplace Activated Batch Norm](https://github.com/mapillary/inplace_abn) from the box, which is essential for reducing memory footprint in segmentation tasks.

## Pretrained models
All default weights from TorchVision repository are supported. There are also weights for modified Resnet family models trained on Imagenet 2012. It's hard to keep this README up to date with new weights, so check the code for all available weight for particular model.  
All models have `pretrained_settings` attribute with training size, mean, std and other useful information about the weights.

## Repositories used
* [Torch Vision Main Repo](https://github.com/pytorch/vision)  
* [Cadene pretrained models](https://github.com/Cadene/pretrained-models.pytorch/)
* [Ross Wightman models](https://github.com/rwightman/pytorch-image-models/)
* [Inplace ABN](https://github.com/mapillary/inplace_abn)
* [Efficient Densenet](https://github.com/gpleiss/efficient_densenet_pytorch)