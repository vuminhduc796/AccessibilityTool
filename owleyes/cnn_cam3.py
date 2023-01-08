import os
import torch.nn as nn
from owleyes.network import Net
import argparse
import cv2
import numpy as np
import torch
from torch.autograd import Function, Variable
from PIL import Image, ImageFile

import app_utils
from owleyes import getdata

ImageFile.LOAD_TRUNCATED_IMAGES = True


class FeatureExtractor():
    """ Class for extracting activations and
    registering gradients from targetted intermediate layers """

    def __init__(self, model, target_layers):
        self.model = model
        self.target_layers = target_layers
        self.gradients = []

    def save_gradient(self, grad):
        self.gradients.append(grad)

    def __call__(self, x):
        outputs = []
        self.gradients = []

        for name, module in self.model.module.features._modules.items():

            x = module(x)

            if name in self.target_layers:
                x.register_hook(self.save_gradient)
                outputs += [x]
        return outputs, x


class ModelOutputs():
    """ Class for making a forward pass, and getting:
    1. The network output.
    2. Activations from intermeddiate targetted layers.
    3. Gradients from intermeddiate targetted layers. """

    def __init__(self, model, target_layers):
        self.model = model
        self.feature_extractor = FeatureExtractor(self.model, target_layers)

    def get_gradients(self):
        return self.feature_extractor.gradients

    def __call__(self, x):
        target_activations, output = self.feature_extractor(x)
        output = output.view(output.size(0), -1)

        return target_activations, output


def preprocess_image(image_file):
    imgs_data = []
    img = Image.open(image_file)

    img_data = getdata.dataTransform(img)
    image_without_alpha = img_data[:3, :, :]
    imgs_data.append(image_without_alpha)
    imgs_data = torch.stack(imgs_data)
    input = Variable(imgs_data, requires_grad=True)
    return input


def show_cam_on_image(img, mask, image_num, output_file_path):
    heatmap = cv2.applyColorMap(np.uint8(255 * mask), cv2.COLORMAP_JET)
    heatmap = np.float32(heatmap) / 255
    cam = heatmap + np.float32(img)
    cam = cam / np.max(cam)
    cv2.imwrite(output_file_path + "/cam.jpg", np.uint8(255 * cam))

    # txtpath = './outputtxt2/{0}.txt'.format(image_num)
    # IMGpath = './examples/{0}.png'.format(image_num)
    # im = Image.open(IMGpath)
    # print(im.size[0])
    # x_num = im.size[0] / 448
    # y_num = im.size[1] / 768

    # gray = cv2.cvtColor(cam,cv2.COLOR_BGR2GRAY)
    # image = gray * 255
    # ret, thresh = cv2.threshold(image, 230, 255, cv2.THRESH_BINARY)
    # cv2.imwrite("0.jpg",thresh)
    # thresh = cv2.imread("0.jpg",cv2.IMREAD_GRAYSCALE)
    # contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #
    #
    # for i in range(0, len(contours)):
    #     x, y, w, h = cv2.boundingRect(contours[i])
    #     if w<10 or h <10:
    #         nnnnn =1
    #     else:
    #         cv2.rectangle(img, (x, y), (x + w, y + h), (153, 153, 0), 1)
    #
    #         xmin = x * x_num
    #         ymin = y * y_num
    #         xmax = (x + w) * x_num
    #         ymax = (y + h) * y_num
    #         with open(txtpath, "a") as ms:
    #             ms.write("component occlusion" + "\n")
    #             ms.write(str(int(xmin)) + "\n")
    #             ms.write(str(int(ymin)) + "\n")
    #             ms.write(str(int(xmax)) + "\n")
    #             ms.write(str(int(ymax)) + "\n")

    # # cv2.imshow("gray1", img)
    # cv2.waitKey(0)
    # cv2.drawContours(img, contours, -1, (0, 0, 255), 1)
    # # cv2.imshow("gray1", img)
    # cv2.waitKey(0)


class GradCam:
    def __init__(self, model, target_layer_names, use_cuda):
        self.model = model
        self.model.eval()
        self.cuda = use_cuda
        if self.cuda:
            self.model = model.cuda()

        self.extractor = ModelOutputs(self.model, target_layer_names)

    def forward(self, input):
        return self.model(input)

    def __call__(self, input, index=None):
        if self.cuda:
            features, output = self.extractor(input.cuda())
        else:
            features, output = self.extractor(input)

        if index == None:
            index = np.argmax(output.cpu().data.numpy())

        one_hot = np.zeros((1, output.size()[-1]), dtype=np.float32)
        one_hot[0][index] = 1
        one_hot = torch.from_numpy(one_hot).requires_grad_(True)
        if self.cuda:
            one_hot = torch.sum(one_hot.cuda() * output)
        else:
            one_hot = torch.sum(one_hot * output)

        self.model.zero_grad()
        one_hot.backward(retain_graph=True)

        grads_val = self.extractor.get_gradients()[-1].cpu().data.numpy()

        target = features[-1]
        target = target.cpu().data.numpy()[0, :]

        weights = np.mean(grads_val, axis=(2, 3))[0, :]
        cam = np.zeros(target.shape[1:], dtype=np.float32)

        for i, w in enumerate(weights):
            cam += w * target[i, :, :]

        cam = np.maximum(cam, 0)
        cam = cv2.resize(cam, (448, 768))
        cam = cam - np.min(cam)
        cam = cam / np.max(cam)
        return cam


class GuidedBackpropReLU(Function):

    @staticmethod
    def forward(self, input):
        positive_mask = (input > 0).type_as(input)
        output = torch.addcmul(torch.zeros(
            input.size()).type_as(input), input, positive_mask)
        self.save_for_backward(input, output)
        return output

    @staticmethod
    def backward(self, grad_output):
        input, output = self.saved_tensors
        grad_input = None

        positive_mask_1 = (input > 0).type_as(grad_output)
        positive_mask_2 = (grad_output > 0).type_as(grad_output)
        grad_input = torch.addcmul(torch.zeros(input.size()).type_as(input),
                                   torch.addcmul(torch.zeros(input.size()).type_as(input), grad_output,
                                                 positive_mask_1), positive_mask_2)

        return grad_input


class GuidedBackpropReLUModel:
    def __init__(self, model, use_cuda):
        self.model = model
        self.model.eval()
        self.cuda = use_cuda
        if self.cuda:
            self.model = model.cuda()

        for idx, module in self.model.module.features._modules.items():
            if module.__class__.__name__ == 'ReLU':
                self.model.module.features._modules[idx] = GuidedBackpropReLU.apply

    def forward(self, input):
        res = self.model.module(input)
        # print(res)
        # print('forward get res')
        return res

    def __call__(self, input, index=None):
        if self.cuda:
            output = self.forward(input.cuda())
        else:
            output = self.forward(input)

        if index == None:
            index = np.argmax(output.cpu().data.numpy())

        one_hot = np.zeros((1, output.size()[-1]), dtype=np.float32)
        one_hot[0][index] = 1
        one_hot = torch.from_numpy(one_hot).requires_grad_(True)
        if self.cuda:
            one_hot = torch.sum(one_hot.cuda() * output)
        else:
            one_hot = torch.sum(one_hot * output)

        one_hot.backward(retain_graph=True)
        output = input.grad.cpu().data.numpy()
        output = output[0, :, :, :]

        return output


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--use-cuda', action='store_true', default=True,
                        help='Use NVIDIA GPU acceleration')
    parser.add_argument('--image-path', type=str, default='./examples/211.jpg',
                        help='Input image path')
    args = parser.parse_args()
    args.use_cuda = args.use_cuda and torch.cuda.is_available()
    # if args.use_cuda:
    #     print("Using GPU for acceleration")
    # else:
    #     print("Using CPU for computation")

    return args


def deprocess_image(img):
    """ see https://github.com/jacobgil/keras-grad-cam/blob/master/grad-cam.py#L65 """
    img = img - np.mean(img)
    img = img / (np.std(img) + 1e-5)
    img = img * 0.1
    img = img + 0.5
    img = np.clip(img, 0, 1)
    return np.uint8(img * 255)

cached = []

def owleyes_scan(currentActivity, newAct, output_dir):
    """ python grad_cam.py <path_to_image>
    1. Loads an image with opencv.
    2. Preprocesses it for VGG19 and converts to a pytorch variable.
    3. Makes a forward pass to find the category index with the highest score,
    and computes intermediate activations.
    Makes the visualization. """

    image_name = newAct + ".png"
    image = os.path.join(output_dir, "activity_screenshots",currentActivity, image_name)
    output_folder = os.path.join(output_dir, "ui_issue_cam",currentActivity,newAct)
    if not os.path.exists(os.path.join(output_dir, "ui_issue_cam")):
        os.mkdir(os.path.join(output_dir, "ui_issue_cam"))
    if not os.path.exists(os.path.join(output_dir, "ui_issue_cam", currentActivity)):
        os.mkdir(os.path.join(output_dir, "ui_issue_cam", currentActivity))
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    print("owl eyes scan")


    model = Net()
    model = nn.DataParallel(model)
    model_dir = os.path.join(output_dir.split("/output")[0],"owleyes")
    # mps for m1 chip
    # "mps" if torch.backends.mps.is_available() else
    model.load_state_dict(torch.load(
        model_dir + "/4model.pth", map_location=torch.device("cpu")))

    grad_cam = GradCam(model=model, target_layer_names=[
                       "40"], use_cuda=False)

    img = cv2.imread(image, 1)
    img = np.float32(cv2.resize(img, (448, 768))) / 255

    input = preprocess_image(image)

    target_index = None
    mask = grad_cam(input, target_index)
    show_cam_on_image(img, mask, newAct, output_folder)
    gb_model = GuidedBackpropReLUModel(model=model, use_cuda=False)
    gb = gb_model(input, index=target_index)

    gb = gb.transpose((1, 2, 0))

    cam_mask = cv2.merge([mask, mask, mask])
    cam_gb = deprocess_image(cam_mask * gb)
    gb = deprocess_image(gb)

    cv2.imwrite(output_folder + "/gb.jpg", gb)
    cv2.imwrite(output_folder + "/cam_gb.jpg", cam_gb)
    print("done: " + output_folder)
    # app_utils.add_new_activity_to_config(
    #     apk_name, emulator_name_android_studio, current_setting, image_num)
def old_owleyes_scan( parent_folder):
    """ python grad_cam.py <path_to_image>
    1. Loads an image with opencv.
    2. Preprocesses it for VGG19 and converts to a pytorch variable.
    3. Makes a forward pass to find the category index with the highest score,
    and computes intermediate activations.
    Makes the visualization. """

    output_folder = 'test_owleye'
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    print("owl eyes scan")
    image_name1 = os.path.join(parent_folder, "examples", "1.png")
    image_name2 = os.path.join(parent_folder, "examples", "2.png")

    model = Net()
    model = nn.DataParallel(model)
    model_dir = os.path.join(parent_folder)
    # mps for m1 chip
    # "mps" if torch.backends.mps.is_available() else
    model.load_state_dict(torch.load(
        model_dir + "/4model.pth", map_location=torch.device("cpu")))

    output_file_path = output_folder + "/test/"
    if not os.path.exists(output_file_path):
        os.mkdir(output_file_path)

    grad_cam = GradCam(model=model, target_layer_names=[
                       "40"], use_cuda=False)

    img1 = cv2.imread(image_name1, 1)
    img2 = cv2.imread(image_name2, 1)
    # image_without_alpha = image_name2[:, :, :3]
    img1 = np.float32(cv2.resize(img1, (448, 768))) / 255
    img2 = np.float32(cv2.resize(img2, (448, 768))) / 255
    input1 = preprocess_image(image_name1)
    input2 = preprocess_image(image_name2)
    print(np.array(img1).shape)
    print(np.array(img2).shape)
    target_index = None
    mask = grad_cam(input1, target_index)
    mask = grad_cam(input2, target_index)
    # show_cam_on_image(img1, mask, image_name1, output_file_path)
    # gb_model = GuidedBackpropReLUModel(model=model, use_cuda=False)
    # gb = gb_model(input, index=target_index)
    #
    # gb = gb.transpose((1, 2, 0))
    #
    # cam_mask = cv2.merge([mask, mask, mask])
    # cam_gb = deprocess_image(cam_mask * gb)
    # gb = deprocess_image(gb)
    #
    # cv2.imwrite(output_file_path + "gb.jpg", gb)
    # cv2.imwrite(output_file_path + "cam_gb.jpg", cam_gb)
    # print("done: " + output_file_path)

if __name__ == '__main__':
    old_owleyes_scan( os.getcwd())