import torchvision.models as models
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = models.vgg19(pretrained=True).features.to(device).eval()
torch.save(model[:11],'vgg19_11_layers.pth')