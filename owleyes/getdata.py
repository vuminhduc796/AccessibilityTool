from PIL import Image,ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import os
import torch.utils.data as data
# from PIL import Image
import numpy as np
import torch
import torchvision.transforms as transforms


# IMAGE_SIZE = 300
#IMAGE_H = 640
#IMAGE_W = 320

#IMAGE_H = 704
#IMAGE_W = 384

IMAGE_H = 768
IMAGE_W = 448
# 定义一个转换关系，用于将图像数据转换成PyTorch的Tensor形式
dataTransform = transforms.Compose([
    transforms.Resize((IMAGE_H,IMAGE_W)),                         
    transforms.CenterCrop((IMAGE_H, IMAGE_W)),        
    transforms.ToTensor() 
])


class Dataset(data.Dataset):   
    def __init__(self, mode, dir):        
        self.mode = mode
        self.list_img = []               
        self.list_label = []             
        self.data_size = 0               
        self.transform = dataTransform     

        if self.mode == 'train':           
            dir = dir + '/train/'          
            for file in os.listdir(dir):  
                print(file)
                self.list_img.append(dir + file)        
                self.data_size += 1                     
                name = file.split(sep='.')              
                if name[0] == 'bug':
                    self.list_label.append(0)        
                else:
                    self.list_label.append(1)       
        elif self.mode == 'test':         
            dir = dir + '/test/'          
            for file in os.listdir(dir):
                self.list_img.append(dir + file)    
                self.data_size += 1
                self.list_label.append(2)      
        else:
            print('Undefined Dataset!')

    def __getitem__(self, item):          
        if self.mode == 'train':                                   
            img = Image.open(self.list_img[item])                     
            label = self.list_label[item]                              

            return self.transform(img), torch.LongTensor([label])      
        elif self.mode == 'test':                                    
            img = Image.open(self.list_img[item])
            return self.transform(img)                            
        else:
            print('None')

    def __len__(self):
        return self.data_size             

