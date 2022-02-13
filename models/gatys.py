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

## НА БАЗЕ АЛГОРИТМА, ПРЕДЛОЖЕННОГО ЛЕОНОМ ГАТИСОМ В 2015 ГОДУ.
## Большая часть кода аналогична примеру в документации pytorch: https://pytorch.org/tutorials/advanced/neural_style_tutorial.html
## За исключением того, что всё завёрнуто в классы
## и изображения приводятся к единому размеру сохраняя aspect ratio, для чего используется паддинг,
## А на выходе изображение "тянется" до исходного размера.

# Класс предобработки изображения(лоадер и геттер)
class ImageProcessing:
    def __init__(self, new_size, device):
        self.new_size = new_size
        self.device = device
        self.image_size = None

    def image_loader(self, image_name):
        image = Image.open(image_name)
        self.image_size = image.size
        # Для сохранения соотношения сторон, ресайзим изображение добавляя паддинг.
        image = PIL.ImageOps.pad(image, (self.new_size, self.new_size))
        loader = transforms.ToTensor()
        image = loader(image).unsqueeze(0)

        return image.to(self.device, torch.float)

    def get_image(self, tensor):
        image = tensor.cpu().clone()
        image = image.squeeze(0)
        unloader = transforms.ToPILImage()
        image = unloader(image)
        # Возвращаем изображению исходный размер.
        image = PIL.ImageOps.fit(image, self.image_size)

        # Записываем изображение в буфер,
        # в таком виде его надо отправлять пользователю
        bio = BytesIO()
        bio.name = 'output.jpeg'
        image.save(bio, 'JPEG')
        bio.seek(0)

        return bio


# Класс вычисления функции потерь для контента
class ContentLoss(nn.Module):
    def __init__(self, target):
        super(ContentLoss, self).__init__()
        self.target = target.detach()  # константа, нужно убрать из вычислительного графа
        self.loss = F.mse_loss(self.target, self.target)  # Инициализируемся исходным изображением

    def forward(self, input):
        self.loss = F.mse_loss(input, self.target)
        return input

# Класс вычисления функции потерь для стиля
class StyleLoss(nn.Module):
    def __init__(self, target_feature):
        super(StyleLoss, self).__init__()
        self.target = self.gram_matrix(target_feature).detach() # константа, нужно убрать из вычислительного графа
        self.loss = F.mse_loss(self.target, self.target)  # Инициализируемся исходным изображением

# Вычисление матрицы Грама. 
# В данном случае реализовал как статический метод, так удобнее , всё зашито в единый класс.
    @staticmethod
    def gram_matrix(input):
        batch_size, feature_maps, h, w = input.size()
        # Вытягиваем в вектор каждую карту признаков
        # Батч-сайз в нашем случае всегда будет 1, потому, что передаем по 1 фото.
        features = input.view(batch_size * feature_maps, h * w)  # resise F_XL into \hat F_XL
        G = torch.mm(features, features.t())  # Вычисляем матрицу Грама.
        # Нормализуем значения в матрице Грама.
        return G.div(batch_size * feature_maps * h * w)

    def forward(self, input):
        gram = self.gram_matrix(input)
        self.loss = F.mse_loss(gram, self.target)
        return input

# Класс нормализации.
# Исходная сетка VGG19 была обучена на сете ImageNet,
# поэтому необходимо все подаваемые на вход изображения нормализовать с такими же средним и стандартным отклонением
class Normalization(nn.Module):
    def __init__(self, device):
        super(Normalization, self).__init__()
        self.mean = torch.tensor([0.485, 0.456, 0.406]).view(-1, 1, 1).to(device)
        self.std = torch.tensor([0.229, 0.224, 0.225]).view(-1, 1, 1).to(device)

    def forward(self, img):
        return (img - self.mean) / self.std

# Основной класс, перенос стиля.
class StyleTransfer:
    def __init__(self, num_steps, device = 'cpu', style_weight=100000, content_weight=1):
        self.num_steps = num_steps
        self.style_weight = style_weight
        self.content_weight = content_weight
        self.device = device

        self.content_layers = ['conv_4']
        self.style_layers = ['conv_1', 'conv_2', 'conv_3', 'conv_4', 'conv_5']

    def get_style_model_and_losses(self, style_img, content_img):
        
        # Загружаем наши сохранённые 11 слоёв от VGG19 и используем как базу для создания сетки.
        cnn = torch.load('./models_wts/vgg19_11_layers.pth', map_location=self.device)
        cnn = cnn.to(self.device).eval()

        normalization = Normalization(self.device).to(self.device)

        content_losses = []
        style_losses = []

        # Начинаем с нормализации
        model = nn.Sequential(normalization)

        # В цикле переименовываем слои.
        # Заменяем ReLU слои, на версию с inplace=False (иначе всё падает)
        i = 0
        for layer in cnn.children():
            if isinstance(layer, nn.Conv2d):
                i += 1
                name = 'conv_{}'.format(i)
            
            elif isinstance(layer, nn.BatchNorm2d):
                name = 'bn_{}'.format(i)
            
            elif isinstance(layer, nn.ReLU):
                name = 'relu_{}'.format(i)   
                layer = nn.ReLU(inplace=False)
            
            elif isinstance(layer, nn.MaxPool2d):
                name = 'pool_{}'.format(i)

            model.add_module(name, layer)

            # Добавляем к указанным слоям контента и стиля - модули лоссов.
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

    # Создаём оптимизатор, инициализируем исходным изображением.
    @staticmethod
    def get_input_optimizer(input_img):
        optimizer = optim.LBFGS([input_img.requires_grad_()])
        return optimizer

    # Непосредственно сам метод реализующий перенос стиля
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

# Функция запуска трансфера стиля. 
def run_nst(style_image, content_image):
    # Определяем доступный девайс
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Определяем максимальный размер масштабирования.
    # Если доступна gpu - 512х512, если нет - 256х256
    RESCALE_SIZE = 512 if torch.cuda.is_available() else 256
    
    # Создаём обработчики для изображений
    style_processing = ImageProcessing(new_size=RESCALE_SIZE, device=device)
    content_processing = ImageProcessing(new_size=RESCALE_SIZE, device=device)

    # Препроцессим изображения
    style_image = style_processing.image_loader(style_image)
    content_image = content_processing.image_loader(content_image)

    # Создаем экземпляр класса StyleTransfer и запускаем сам перенос стиля
    # После чего возвращаем изображению исходный размер и сохраняем в ByteIO
    transfer = StyleTransfer(num_steps=200, device=device)
    output = transfer.transfer_style(style_image, content_image)
    output = content_processing.get_image(output)

    return output