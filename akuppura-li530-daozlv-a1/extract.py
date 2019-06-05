
import argparse
from PIL import Image, ImageOps
from Filter import Filter
from Detector import Detector
import numpy as np
from PIL import Image





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("injected_img")
    parser.add_argument("output_txt")
    args = parser.parse_args()


'''
Common variables
'''
CHOICES=['','A','B','C','D','E','']
DUMMY=[0 for i in range(7)]
ZOOM=8
QUESTION_CNT=85
HEADER_CNT=len(CHOICES)
START_C = 260
START_R = 450
SECRET=[0,0,0,0,0]
searchval = 5

def get_secret(secret_array):
    """
    Get the secret number from the barcode
    :param secret_array:
    :return:
    """
    for k,i in enumerate(secret_array):
        #print (k,i)
        SECRET[k]=i.index(max(i))-1## As we are adding 0's in the starting and ending to define the border

def get_ans(ans_array):
    """
    Function to parse the answer np array
    :param ans_array:
    :return: answer values
    """
    answers_tmp = []
    for q, i in enumerate(ans_array):
        tmp = []
        # print i
        for k, j in enumerate(inverse_disperse(SECRET,i)):
            if j >= 230:  # To accomodate any loss in intensity of white(255)
                tmp.append(CHOICES[k])
        answers_tmp.append(tmp)
    return answers_tmp

def write_ans(fl_nm,answers):
    """
    Function to write the answers to an output file
    :param fl_nm: File name
    :param answers: Answer text
    :return:
    """
    with open(fl_nm, "w") as f:
        for i in range(len(answers)):
            f.write(str((i + 1)) + " " + ''.join(answers[i]) + "\n")

def inverse_disperse(SECRET_NO,lst):
    """
    Implementation to inverse the dispersion function
    :param SECRET_NO: secret text
    :param lst: data list
    :return: Correct list
    """
    tmp=[0,0,0,0,0,0,0]
    lst=lst[1:-1]
    for k,i in enumerate(SECRET_NO):
        tmp[i+1]=lst[k]
    return tmp

#Load image


img=np.array(Image.open(args.injected_img))

#Select the specific location containing the barcode.
src_array=img[START_R:START_R+len(CHOICES)*ZOOM,START_C:START_C+(QUESTION_CNT+HEADER_CNT)*ZOOM]#[:,:]
#print src_array[39:52,6:19]

#Load the CODE_LST array
CODED_LST=[]
for col in range(0,src_array.shape[1],ZOOM):
    tmp = []
    for row in range(0,src_array.shape[0],ZOOM):
        tmp.append(src_array[row,col])
    CODED_LST.append(tmp)

#Seperate the SECRET CODE
secret_array=CODED_LST[1:len(SECRET)+1]

#Seperate the answer array
ans_array=CODED_LST[len(SECRET)+1:-1]

get_secret(secret_array)
print(SECRET)

#Get actual answers from the answers array
answers=get_ans(ans_array)

#Write answers to the output file
write_ans(args.output_txt,answers)
