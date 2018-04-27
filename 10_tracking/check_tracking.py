#!/usr/bin/env python
# -* coding:utf-8 *-

import cv2
import argparse
import os
import glob
import csv
from tqdm import tqdm
from time import sleep

def write(x, img):
    c1 = tuple(map(int,x[0:4]))
    c2 = tuple(map(int,x[2:4]))
    cv2.rectangle(img, c1, c2, "green", 1)

    t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 1 , 1)[0]
    c2 = c1[0] + t_size[0] + 3, c1[1] + t_size[1] + 4
    cv2.rectangle(img, c1, c2,color, -1)
    cv2.putText(img, label, (c1[0], c1[1] + t_size[1] + 4), cv2.FONT_HERSHEY_PLAIN, 1, [225,255,255], 1);

    return img


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--day", required=True)
    parser.add_argument("--base_hour", type=int, required=True)
    parser.add_argument("--hours", type=int, required=True)
    args = parser.parse_args()

    img_rootd = '../00_data/pics'

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out_dir = '../00_data/videos/'+args.day
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    last_hour = args.base_hour + args.hours

    for hour in range(args.base_hour, last_hour):

        hour = '%02d' % hour
        img_dir = img_rootd+'/'+args.day+'/'+args.day+hour
        img_list = sorted(glob.glob(os.path.join(img_dir, '*')))

        video_path = out_dir+'/'+args.day+hour+'_pre.avi'

        video = cv2.VideoWriter(video_path, fourcc, 20.0, (800, 600))

        coords_file = './10_tracking/'+args.day+'/'+args.day+hour+'_0.csv'
        with open(coords_file, 'r') as f:
            reader = csv.reader(f)
            cows = [ row for row in reader ]

        print(args.day+":"+hour+"----------")

        pre_c1 = tuple(map(int,cows[0][1:3]))
        pre_c2 = tuple(map(int,cows[0][3:5]))

        for cow in tqdm(cows):
            #print(cow[0])
            img = cv2.imread(cow[0],1)
            cv2.rectangle(img, pre_c1, pre_c2, (255,0,0), 2)

            iou = cow[-1]

            if len(cow) != 1:
                c1 = tuple(map(int,cow[1:3]))
                c2 = tuple(map(int,cow[3:5]))
                cv2.rectangle(img, c1, c2, (0,0,255), 2)
                pre_c1 = c1
                pre_c2 = c2

                t_size = cv2.getTextSize(iou, cv2.FONT_HERSHEY_PLAIN, 1 , 1)[0]
                c2 = c1[0] + t_size[0] + 3, c1[1] + t_size[1] + 4
                cv2.rectangle(img, c1, c2, (0,0,255), -1)
                cv2.putText(img, iou, (c1[0], c1[1] + t_size[1] + 4), cv2.FONT_HERSHEY_PLAIN, 1, [225,255,255], 1);

            #sleep(0.05)
            #cv2.imshow('img',img)
            video.write(img)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break

        video.release()
