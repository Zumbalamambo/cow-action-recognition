import numpy as np
import cv2
from util import *
from bbox import bbox_iou2
import pandas as pd
import random
import argparse
import csv
import os
import glob
import queue
from tqdm import tqdm

def inc_cow(bbox_, cow_coords):
    iou_thesh = 0.7
    iou_over = 0
    for cow_coord in cow_coords:
        iou = bbox_iou2(bbox_, cow_coord)
        if iou > iou_thesh:
            iou_over += 1
        if iou == 0.0 and len(cow_coords) <= max_num_cow:
            return True
        if iou_over == max_num_cow:
            return False
    return False

def arg_parse():
    parser = argparse.ArgumentParser(description='YOLO v3 Video Detection Module')
    parser.add_argument("--day", required = True)
    parser.add_argument("--base_hour", type = int, required = True)
    parser.add_argument("--hours", type = int, required = True)
    return parser.parse_args()

if __name__ == '__main__':
    args = arg_parse()
    #confidence = float(args.confidence)
    #nms_thesh = float(args.nms_thresh)

    iou_thesh = 0.7

    img_rootd = '../00_data/pics/'+args.day
    coord_dir = './00_coords/' + args.day
    out_dir = './10_tracking/' + args.day

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    last_hour = args.base_hour + args.hours

    for hour in range(args.base_hour, last_hour):

        hour = str('%02d' % hour)
        detection_file = coord_dir + '/' + args.day+hour + '.csv'
        print(detection_file,'--------------')
        f = open(detection_file, 'r')
        reader = csv.reader(f)

        # 牛の初期位置を覚えとく，適宜追加
        cows = []
        for row in reader:
            cows_init = row
            break
        max_num_cow = 2
        num_cow_init = int((len(cows_init)-1)/4)
        cows_coords = []
        for i in range(num_cow_init):
            cows_coords.append([cows_init[i*4+1], cows_init[i*4+2], cows_init[i*4+3], cows_init[i*4+4]])

        num_cow = num_cow_init
        cow = 1
        while cow < 2:
            with open(out_dir+'/'+args.day+hour+'_'+str(cow-1)+'.csv', 'w') as f:
                writer = csv.writer(f, lineterminator='\n')
                print('cow-number:',str(cow))
                pre_bbox = cows_coords[cow-1]
                for cows in tqdm(reader):
                    num_bbox = int((len(cows)-1)/4)
                    bboxes = [ [cows[i*4+1], cows[i*4+2], cows[i*4+3], cows[i*4+4] ] for i in range(num_bbox) ]
                    # 牛が増えた時,既にいる奴とIoU計算して，一番小さい座標の牛個体追加
                    if num_cow < num_bbox:
                        # 各ボックスのIoU計算，IoUが0があったらそいつを追加，全部どれかを超えてたら追加なし
                        for bbox_ in bboxes:
                            if inc_cow(bbox_, cows_coords):
                                cows_coords.append(bbox_)
                                break
                    ious = []
                    for bbox in bboxes:
                        ious.append(bbox_iou2(bbox,pre_bbox))
                    line = [cows[0]] + bboxes[ious.index(max(ious))]
                    writer.writerow(line)
                    pre_bbox = bboxes[ious.index(max(ious))]
            cow += 1
        f.close()


        '''
        img_dir = img_rootd+'/'+args.day+str('%02d' % hour)
        img_list = sorted(glob.glob(os.path.join(img_dir, '*')))

        out_file = out_dir + '/' + args.day + str('%02d' % hour) + '.csv'
        print(out_file, "-----------------")
        with open(out_file, 'w') as f:
            writer = csv.writer(f, lineterminator='\n')

            for img_path in tqdm(img_list):
            #for img_path in img_list:
                img, orig_im, dim = prep_image(img_path, inp_dim)
                im_dim = torch.FloatTensor(dim).repeat(1,2)

                if CUDA:
                    im_dim = im_dim.cuda()
                    img = img.cuda()

                output = model(Variable(img, volatile = True), CUDA)
                output = write_results(output, confidence, num_classes, nms = True, nms_conf = nms_thesh)

                if type(output) == int:
                    frames += 1
                    #out.write(orig_im)
                    #cv2.imshow("frame", orig_im)
                    continue

                coords = [ list(map(int, x[1:5])) for x in output ]
                coords_all = [img_path]
                for coord in coords:
                    coords_all += coord
                writer.writerow(coords_all)

                #cv2.imshow("frame", orig_im)
        '''
