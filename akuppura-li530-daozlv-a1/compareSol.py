from PIL import Image, ImageOps
import argparse
from PIL import Image, ImageOps
from Filter import Filter
from Detector import Detector
import numpy as np
from matplotlib.pyplot import imshow
from itertools import combinations

import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import random


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_im")
    parser.add_argument("correct_ans_txt")
    args = parser.parse_args()

    text_file = open(args.input_im, "r")
    linesInput = text_file.readlines()
    text_file.close()

    text_file = open(args.correct_ans_txt, "r")
    linesAns = text_file.readlines()
    text_file.close()
    wrongNum = 0
    for i in range (len(linesAns)):
        if linesAns[i] != linesInput[i]:
            wrongNum += 1
    wrongNum = wrongNum/(len(linesAns))
    print(wrongNum)
        
