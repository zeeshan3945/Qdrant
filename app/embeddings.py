import os
import torch
from torchvision import transforms
from PIL import Image
import numpy as np
import requests
from io import BytesIO


#model=torch.load('models/Mgg16_Model.pt')
class Embeddings:
    def __init__(self):
        self.normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
        )

        self.tr = transforms.Compose(
            [transforms.Resize(256), transforms.ToTensor(), self.normalize,]
        )

        self.model = torch.jit.load('Vgg16_Model')

    def get_embedding(self, path):

        # if os.path.exists(path):
        #     PIL_image = Image.open(path).convert(
        #         "RGB"
        #     )  # Converting to RGB, as some images in dataset are greyscale

        # if path[:4] == 'http':
        #     response = requests.get(url=path)
        #     PIL_image = Image.open(BytesIO(response.content)).convert(
        #         "RGB"
        #     )
        PIL_image = path  #Uncomment and run when running code for byte streams
        img_tensor = self.tr(PIL_image)
        img_expanded = torch.unsqueeze(img_tensor, dim=0)
        self.model.eval()
        out = np.squeeze(self.model(img_expanded).detach().cpu()).tolist()
        return out

    def get_embeddings_across_imgs(self, images_path):
        imgs_path = self.get_img_paths(images_path)
        embeddings = []
        for img in imgs_path:
            embedding_img = self.get_embedding(img)
            embeddings.append(embedding_img)
        return embeddings

    def get_img_paths(self, imgs_path):
        imgs_paths = []
        if ".jpg" in imgs_path:
            imgs_paths.append(imgs_path)
        else:
            for file in os.listdir(imgs_path):
                if ".jpg" in file:
                    img_path = os.path.join(imgs_path, file)
                    imgs_paths.append(img_path)
        return imgs_paths


# images_path = "/home/ahmad/Downloads/Qdrant_images/coin_data/coin_images"
# embeddings = Embeddings()
# image_path = "/Users/zeeshan/Desktop/Qdrant/Qdrant/test-images/00000146.jpg"
# img = Image.open(image_path)
# print(embeddings.get_embedding(img))

# points_list = embeddings.get_embeddings_across_imgs(images_path)