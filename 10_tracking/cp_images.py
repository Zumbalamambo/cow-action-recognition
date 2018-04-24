#!/usr/bin/env python
# -* coding:utf-8 *-

import cv2
import argparse
import os
import glob
import shutil
from tqdm import tqdm

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--day", required=True)
    args = parser.parse_args()

    if not os.path.exists('../00_data/videos/'+args.day):
        os.makedirs('../00_data/videos/'+args.day)

    if not os.path.exists('../00_data/pics/'+args.day):
        os.makedirs('../00_data/pics/'+args.day)

    img_rootd = '/var/docker/data/cow/pics'

    for hour in range(24):
        hour = '%02d' % hour
        img_dir = img_rootd+'/'+args.day+'/'+args.day+hour
        img_list = sorted(glob.glob(os.path.join(img_dir, '*')))

        if not os.path.exists('../00_data/pics/'+args.day+'/'+hour):
            os.makedirs('../00_data/pics/'+args.day+'/'+hour)
        out_dir = '../00_data/pics/'+args.day+'/'+hour

        print(args.day+":"+hour+"----------")

        for i in tqdm(range(0, 200)):
            img_path = img_list[i]
            out_path = out_dir + img_path.split("/")[-1]
            shutil.copy(img_path, out_path)
