from os import listdir
import sys
import os
import cv2


def map_snitching(path):
    img_paths = listdir(path)
    assert len(img_paths) == 9
    imgs = []
    for img_name in img_paths:
        img = cv2.imread(path + "\\" + img_name)
        if img is None:
            print("can't read image " + img_name)
            sys.exit(-1)
        imgs.append(img)
    # stitcher = cv2.createStitcher(cv2.Stitcher_PANORAMA)  # cv.Stitcher_SCANS
    # status, pano = stitcher.stitch(imgs)
    out_path = os.path.join(path, 'result1.png')
    # cv2.imwrite(out_path, pano)
    # for test
    cnt_result = 500

    return cnt_result
