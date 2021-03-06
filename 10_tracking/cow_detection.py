import torch
import torch.nn as nn
from torch.autograd import Variable
import numpy as np
import cv2
from util import *
from darknet import Darknet
import pandas as pd
import random
import pickle as pkl
import argparse
import csv
import os
import glob
from tqdm import tqdm


def get_test_input(input_dim, CUDA):
    img = cv2.imread("dog-cycle-car.png")
    img = cv2.resize(img, (input_dim, input_dim))
    img_ =  img[:,:,::-1].transpose((2,0,1))
    img_ = img_[np.newaxis,:,:,:]/255.0
    img_ = torch.from_numpy(img_).float()
    img_ = Variable(img_)

    if CUDA:
        img_ = img_.cuda()

    return img_

def prep_image(img_path, inp_dim):
    """
    Prepare image for inputting to the neural network. Returns a Variable
    """
    orig_im = cv2.imread(img_path)
    dim = orig_im.shape[1], orig_im.shape[0]
    img = cv2.resize(orig_im, (inp_dim, inp_dim))
    img_ = img[:,:,::-1].transpose((2,0,1)).copy()
    img_ = torch.from_numpy(img_).float().div(255.0).unsqueeze(0)
    return img_, orig_im, dim

def write(x, img):
    c1 = tuple(x[1:3].int())
    c2 = tuple(x[3:5].int())
    cls = int(x[-1])
    label = "{0}".format(classes[cls])
    color = random.choice(colors)
    #print(c1, c2, label)
    cv2.rectangle(img, c1, c2,color, 1)
    return img

def is_animal(x):
    cls = int(x[-1][-1])
    label = "{0}".format(classes[cls])
    if label in animals:
        return True
    else:
        return False

def arg_parse():
    parser = argparse.ArgumentParser(description='YOLO v3 Video Detection Module')

    parser.add_argument("--day", required = True)
    parser.add_argument("--base_hour", type = int, required = True)
    parser.add_argument("--hours", type = int, required = True)
    #parser.add_argument("--video", dest = 'video', help = "Video to run detection upon", default = "video.avi", type = str)
    #parser.add_argument("--dataset", dest = "dataset", help = "Dataset on which the network has been trained", default = "pascal")
    parser.add_argument("--confidence", dest = "confidence", help = "Object Confidence to filter predictions", default = 0.5)
    parser.add_argument("--nms_thresh", dest = "nms_thresh", help = "NMS Threshhold", default = 0.4)
    parser.add_argument("--cfg", dest = 'cfgfile', help ="Config file", default = "cfg/yolov3.cfg", type = str)
    parser.add_argument("--weights", dest = 'weightsfile', help = "weightsfile", default = "yolov3.weights", type = str)
    parser.add_argument("--reso", dest = 'reso', help = "Input resolution of the network. Increase to increase accuracy. Decrease to increase speed",
                        default = "416", type = str)
    return parser.parse_args()

if __name__ == '__main__':
    args = arg_parse()
    confidence = float(args.confidence)
    nms_thesh = float(args.nms_thresh)

    classes = load_classes('data/coco.names')
    colors = pkl.load(open("pallete", "rb"))

    animals = [
        'bird','cat','dog','horse','sheep','cow','elephant','bear','zebra','giraffe',
    ]

    CUDA = torch.cuda.is_available()

    num_classes = 80

    CUDA = torch.cuda.is_available()

    print("Loading network.....")
    model = Darknet(args.cfgfile)
    model.load_weights(args.weightsfile)
    print("Network successfully loaded")

    model.net_info["height"] = args.reso
    inp_dim = int(model.net_info["height"])
    assert inp_dim % 32 == 0
    assert inp_dim > 32

    if CUDA:
        model.cuda()

    model(get_test_input(inp_dim, CUDA), CUDA)

    model.eval()

    img_rootd = '../00_data/pics/'+args.day

    out_dir = './00_coords/' + args.day

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    last_hour = args.base_hour + args.hours

    for hour in range(args.base_hour, last_hour):
        img_dir = img_rootd+'/'+args.day+str('%02d' % hour)
        img_list = sorted(glob.glob(os.path.join(img_dir, '*')))

        out_file = out_dir + '/' + args.day + str('%02d' % hour) + '.csv'
        print(out_file, "-----------------")
        with open(out_file, 'w') as f:
            writer = csv.writer(f, lineterminator='\n')

            for img_path in tqdm(img_list):
                img, orig_im, dim = prep_image(img_path, inp_dim)
                im_dim = torch.FloatTensor(dim).repeat(1,2)

                if CUDA:
                    im_dim = im_dim.cuda()
                    img = img.cuda()

                output = model(Variable(img, volatile = True), CUDA)
                output = write_results(output, confidence, num_classes, nms = True, nms_conf = nms_thesh)

                if type(output) == int:
                    continue

                if is_animal(output):
                    output[:,1:5] = torch.clamp(output[:,1:5], 0.0, float(inp_dim))

                    im_dim = im_dim.repeat(output.size(0), 1)/inp_dim
                    output[:,1:5] *= im_dim

                    coords = [ list(map(int, x[1:5])) for x in output ]
                    coords_all = [img_path]
                    for coord in coords:
                        coords_all += coord
                    writer.writerow(coords_all)
                else:
                    coords_all = [img_path]
                    writer.writerow(coords_all)
