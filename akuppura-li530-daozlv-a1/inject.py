
import argparse
from PIL import Image, ImageOps
from Filter import Filter
from Detector import Detector
import numpy as np


from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import random


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_im")
    parser.add_argument("ans_txt")
    parser.add_argument("injected_img")
    args = parser.parse_args()


    '''
    Common variables
    '''
    CHOICES = ['', 'A', 'B', 'C', 'D', 'E', '']
    DUMMY = [0 for i in range(7)]
    SECRET = random.sample(range(0,5), 5)
    START_C = 260
    START_R = 450
    ZOOM_FACTOR=8
    EXTRA_CHARS=[str(i) for i in range(10)]+[' ']+['']+[',']+[':']+['\n']


    def insert_msg(img, msg):
        """
        :param img: Image
        :param msg: Text to be inserted
        :return: Image object
        """
        font = ImageFont.truetype("Arial.ttf", 20)
        image = ImageOps.grayscale(img)
        draw = ImageDraw.Draw(image)
        draw.text((240, 350), msg, (0), font=font)
        draw = ImageDraw.Draw(image)
        return image


    def insert_barcode(img_array, START_C, START_R, insrt_array):
        """
        :param img_array: Image as np array
        :param START_C: column - Pixel value to insert bar code
        :param START_R: Row - Pixel value to insert bar code
        :param insrt_array: Data array with values
        :return: Image array
        """
        j = np.kron(insrt_array, np.ones((ZOOM_FACTOR, ZOOM_FACTOR))).transpose()
        img_array[START_R:START_R + j.shape[0], START_C:START_C + j.shape[1]] = j
        return Image.fromarray(img_array, 'L')




    def read_ans_txt(fl_nm):
        """

        :param fl_nm: File name containing the answer
        :return: Filtered list with the answer
        """
        lst = []
        with open(fl_nm, "r") as f:
            for i, v in enumerate(f):
                #print (''.join(filter(str.isalpha,v.split())))
                #print (list(filter(lambda x: x not in EXTRA_CHARS ,v)))
                lst.append(list(filter(lambda x: x not in EXTRA_CHARS ,v)))
        return lst




    def SECRET_HEADER(SECRET):
        """
        Prepare secret header to hide the answer encoding
        :param SECRET: list of secret value
        :return: data list
        """
        HEADER = []
        tmp = [0 for i in range(7)]
        for i in SECRET:
            tmp[i + 1] = 255
            HEADER.append(tmp[:])
            tmp[i + 1] = 0
        return HEADER


    def disperse(SECRET_POSITION, lst):
        """
        Disperse the data list based on SECRET lst
        :param SECRET_POSITION: SECRET text
        :param lst:
        :return: dispersed list
        """
        i = [0]  # Border bit
        i.extend(np.array(lst[1:len(CHOICES) - 1])[SECRET])
        i.append(lst[-1])  # Border bit
        return i

#Step 1: Add Header and secret no

    CODED_LST = []
    CODED_LST.extend([DUMMY])
    CODED_LST.extend(SECRET_HEADER(SECRET))

# Step 2: Read Answer text add to lst
    ans_lst = read_ans_txt(args.ans_txt)
    tmp = []
    for i in ans_lst:

        tmp.extend([255 if i.count(u) == 1 else 0 for u in CHOICES])
        CODED_LST.append(disperse(SECRET,tmp))
        tmp = []

# Step 3: Add trailer lst
    CODED_LST.extend([DUMMY])

#Step 4 : Read Image
    image = Image.open(args.input_im).convert('RGB')

#Step 5 : Insert Message and Barcode and write the injected image
    a = np.array(insert_msg(image, 'SECRET CODE - '+" ".join(str(x) for x in SECRET)))
    insert_barcode(a, START_C, START_R, CODED_LST).save(args.injected_img)
