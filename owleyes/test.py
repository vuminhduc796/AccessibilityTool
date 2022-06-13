
from PIL import Image,ImageFile
from sklearn import metrics
ImageFile.LOAD_TRUNCATED_IMAGES = True
from network import Net
import torch
import numpy as np
import torch.nn.functional as F
import torch.nn as nn
import os
import getdata


dataset_dir = './data/test/'                    
model_path = './'
ori_pic_dir= './data/test/'
new_dir='./output/test/'
acc_path = './record/acc.txt'

def test(count):
    count1 = str(count)
    with open(acc_path, "a+") as acc_f:
        model_file = model_path + '%d'%count +'model.pth'
        model = Net()
        model.cuda()
        model = nn.DataParallel(model)
        model.load_state_dict(torch.load(model_file))
        model.eval()

        files = os.listdir(dataset_dir)
        imgs = []
        imgs_data = []
        out1 = []
        for file in files:

            img = Image.open(dataset_dir + file)
            img_data = getdata.dataTransform(img)

            imgs_data.append(img_data)
            imgs_data = torch.stack(imgs_data)

            out = model(imgs_data)
            print(out)
            out = F.softmax(out, dim=1)
            out = out.data.cpu().numpy()
            out2 = out[0]
            out1.append(out2)
            imgs_data = []

        out3 = np.array(out1)
        print(out3)

        wrong_end = []
        true_end = []
        name = []
        x = []
        x_c = []
        x_d = []
        y = []
        y_c = []
        y_d = []

        for idx in range(len(files)):
            a = files[idx]
            (filename, extension) = os.path.splitext(a)
            b = int(filename)
            name.append(b)


            if b < 20000:
                y.append(1)
                y_c.append(1)
                if out3[idx, 0] > out3[idx, 1]:
                    x.append(1)
                    x_c.append(1)
                else:
                    x.append(0)
                    x_c.append(0)
            else:
                y.append(0)
                y_d.append(0)
                if out3[idx, 0] > out3[idx, 1]:
                    x.append(1)
                    x_d.append(1)
                else:
                    x.append(0)
                    x_d.append(0)
        print(x)
        print(y)

        p = metrics.precision_score(y, x)
        r = metrics.recall_score(y, x)
        f1 = metrics.f1_score(y, x)
        a = metrics.accuracy_score(y, x)

        print('precision: %f' % p)
        print('recall: %f' % r)
        print('f1_score: %f' % f1)
        print('accuracy: %f' % a)

        a_c = metrics.accuracy_score(y_c, x_c)
        a_d = metrics.accuracy_score(y_d, x_d)

        print('bug accuracy: %f' % a_c)
        print('normal accuracy: %f' % a_d)



if __name__ == '__main__':
    test(4)
