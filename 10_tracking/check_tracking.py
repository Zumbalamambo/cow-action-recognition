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
    return img

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--day", required=True)
    parser.add_argument("--hour", type=int, required=True)
    args = parser.parse_args()

    img_rootd = '../00_data/pics'

    hour = '%02d' % args.hour
    img_dir = img_rootd+'/'+args.day+'/'+args.day+hour
    img_list = sorted(glob.glob(os.path.join(img_dir, '*')))

    coords_file = './10_tracking/'+args.day+'/'+args.day+hour+'_0.csv'

    #video_path = '../00_data/videos/'+args.day+'/'+args.day+str('%02d' % args.hour)+'.avi'
    #print(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out_dir = '../00_data/videos/'+args.day
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    video_path = out_dir+'/'+args.day+str('%02d' % args.hour)+'.avi'

    video = cv2.VideoWriter(video_path, fourcc, 20.0, (800, 600))

    with open(coords_file, 'r') as f:
        reader = csv.reader(f)
        cows = [ row for row in reader ]

    print(args.day+":"+hour+"----------")

    for cow in tqdm(cows):
        #print(cow[0])
        img = cv2.imread(cow[0],1)

        c1 = tuple(map(int,cow[1:3]))
        c2 = tuple(map(int,cow[3:5]))
        cv2.rectangle(img, c1, c2, (0,0,255), 2)

        #sleep(0.05)
        #cv2.imshow('img',img)
        video.write(img)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break

    video.release()
