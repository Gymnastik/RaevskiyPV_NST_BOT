from PIL import Image
import PIL
import copy

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision.models as models

import torchvision.transforms as transforms
from io import BytesIO
import logging
logging.basicConfig(level=logging.INFO)


class ImageProcessing:
    def __init__(self, new_size, device):
        self.new_size = new_size
        self.device = device
        self.image_size = None

    def image_loader(self, image_name):
        image = Image.open(image_name)
        self.image_size = image.size
        image = PIL.ImageOps.pad(image, (self.new_size, self.new_size))
        loader = transforms.ToTensor()
        image = loader(image).unsqueeze(0)

        return image.to(self.device, torch.float)

    def get_image(self, tensor):
        image = tensor.cpu().clone()
        image = image.squeeze(0)
        unloader = transforms.ToPILImage()
        image = unloader(image)
        image = PIL.ImageOps.fit(image, self.image_size)

        # transform PIL image to send to telegram
        bio = BytesIO()
        bio.name = 'output.jpeg'
        image.save(bio, 'JPEG')
        bio.seek(0)

        return bio


class ContentLoss(nn.Module):
    def __init__(self, target):
        super(ContentLoss, self).__init__()
        self.target = target.detach()  # это константа. Убираем ее из дерева вычислений
        self.loss = F.mse_loss(self.target, self.target)  # to initialize with something

    def forward(self, input):
        self.loss = F.mse_loss(input, self.target)
        return input


class StyleLoss(nn.Module):
    def __init__(self, target_feature):
        super(StyleLoss, self).__init__()
        self.target = self.gram_matrix(target_feature).detach()
        self.loss = F.mse_loss(self.target, self.target)  # to initialize with something

    @staticmethod
    def gram_matrix(input):
        batch_size, h, w, f_map_num = input.size()
        features = input.view(batch_size * h, w * f_map_num)  # resise F_XL into \hat F_XL
        G = torch.mm(features, features.t())  # compute the gram product
        # we 'normalize' the values of the gram matrix
        # by dividing by the number of element in each feature maps.
        return G.div(batch_size * h * w * f_map_num)

    def forward(self, input):
        gram = self.gram_matrix(input)
        self.loss = F.mse_loss(gram, self.target)
        return input


class Normalization(nn.Module):
    def __init__(self, device):
        super(Normalization, self).__init__()
        self.mean = torch.tensor([0.485, 0.456, 0.406]).view(-1, 1, 1).to(device)
        self.std = torch.tensor([0.229, 0.224, 0.225]).view(-1, 1, 1).to(device)

    def forward(self, img):
        return (img - self.mean) / self.std


class StyleTransfer:
    def __init__(self, num_steps, device = 'cpu', style_weight=100000, content_weight=1):
        self.num_steps = num_steps
        self.style_weight = style_weight
        self.content_weight = content_weight
        self.device = device

        self.content_layers = ['conv_4']
        self.style_layers = ['conv_1', 'conv_2', 'conv_3', 'conv_4', 'conv_5']

    def get_style_model_and_losses(self, style_img, content_img):
        # vgg19
        cnn = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False),
            nn.Conv2d(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.ReLU(),
            nn.Conv2d(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False),
            nn.Conv2d(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        )
        
        cnn.load_state_dict(torch.load("models_wts/vgg19_11_layers.pth", map_location=torch.device(self.device)))
        cnn = cnn.to(self.device).eval()

        normalization = Normalization(self.device).to(self.device)

        content_losses = []
        style_losses = []

        model = nn.Sequential(normalization)

        i = 0
        for layer in cnn.children():
            if isinstance(layer, nn.Conv2d):
                i += 1
                name = 'conv_{}'.format(i)
            elif isinstance(layer, nn.BatchNorm2d):
                name = 'bn_{}'.format(i)
            elif isinstance(layer, nn.ReLU):
                name = 'relu_{}'.format(i)
            elif isinstance(layer, nn.MaxPool2d):
                name = 'pool_{}'.format(i)

            model.add_module(name, layer)

            if name in self.content_layers:
                target = model(content_img).detach()
                content_loss = ContentLoss(target)
                model.add_module("content_loss_{}".format(i), content_loss)
                content_losses.append(content_loss)

            if name in self.style_layers:
                target_feature = model(style_img).detach()
                style_loss = StyleLoss(target_feature)
                model.add_module("style_loss_{}".format(i), style_loss)
                style_losses.append(style_loss)

        return model, style_losses, content_losses

    @staticmethod
    def get_input_optimizer(input_img):
        optimizer = optim.LBFGS([input_img.requires_grad_()])
        return optimizer

    def transfer_style(self, style_img, content_img):
        input_img = content_img.clone()
        model, style_losses, content_losses = self.get_style_model_and_losses(
            style_img, content_img)
        optimizer = self.get_input_optimizer(input_img)

        run = [0]
        while run[0] <= self.num_steps:

            def closure():
                input_img.data.clamp_(0, 1)

                optimizer.zero_grad()

                model(input_img)

                style_score = 0
                content_score = 0

                for sl in style_losses:
                    style_score += sl.loss
                for cl in content_losses:
                    content_score += cl.loss

                style_score *= self.style_weight
                content_score *= self.content_weight
                loss = style_score + content_score
                loss.backward()

                if run[0] % 50 == 0:
                    logging.info(f"run: {run[0]}")
                run[0] += 1

                return style_score + content_score

            optimizer.step(closure)

        input_img.data.clamp_(0, 1)

        return input_img

def run_nst(style_image, content_image):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    style_processing = ImageProcessing(new_size=250, device=device)
    content_processing = ImageProcessing(new_size=250, device=device)

    style_image = style_processing.image_loader(style_image)
    content_image = content_processing.image_loader(content_image)

    transfer = StyleTransfer(num_steps=200, device=device)
    output = transfer.transfer_style(style_image, content_image)
    output = content_processing.get_image(output)

    return output