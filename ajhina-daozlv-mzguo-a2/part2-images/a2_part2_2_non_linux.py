from PIL import Image
import numpy as np
import math
import sys

def affine_transform(image_array, transformation_matrix):
    value, width, height = image_array.shape
    # print(image_array[:, 1, 1])
    #     max_dim = max(height, width)
    T = transformation_matrix
    image_list_prime = []

    row_min = 999999
    row_max = -999999
    col_min = 999999
    col_max = -999999

    for row in range(0, height):
        for col in range(0, width):
            pixel_vector = np.array([[col], [row], [1]])
            col_prime, row_prime, w = np.dot(T, pixel_vector)
            row_prime = row_prime / w  # convert 3-d homogeneous coordinate back to 2-d cartesian coordiante
            col_prime = col_prime / w
            image_list_prime.append([col_prime, row_prime, col, row])  # image_array[:, col, row]

            if row_prime < row_min:
                row_min = row_prime
            if row_prime > row_max:
                row_max = row_prime
            if col_prime < col_min:
                col_min = col_prime
            if col_prime > col_max:
                col_max = col_prime

    height_prime = int(row_max - row_min) + 2
    width_prime = int(col_max - col_min) + 2
    # print(height_prime, width_prime)
    image_list_prime = image_list_prime - np.array([col_min, row_min, 0, 0])
    image_array_prime = np.zeros((3, width_prime, height_prime))

    for i, j, k, l in image_list_prime:
        centered = [i == math.floor(i), j == math.floor(j)]
        if centered[0] and centered[1]:
            image_array_prime[:, int(i), int(j)] = list(image_array[:, int(k), int(l)])
        elif not centered[0] and centered[1]:
            image_array_prime[:, int(math.floor(i)), int(j)] = list(image_array[:, int(k), int(l)])
            image_array_prime[:, int(math.ceil(i)), int(j)] = list(image_array[:, int(k), int(l)])
        elif centered[0] and not centered[1]:
            image_array_prime[:, int(i), int(math.floor(j))] = list(image_array[:, int(k), int(l)])
            image_array_prime[:, int(i), int(math.ceil(j))] = list(image_array[:, int(k), int(l)])
        else:
            image_array_prime[:, int(i), int(math.floor(j))] = list(image_array[:, int(k), int(l)])
            image_array_prime[:, int(i), int(math.ceil(j))] = list(image_array[:, int(k), int(l)])
            image_array_prime[:, int(math.floor(i)), int(j)] = list(image_array[:, int(k), int(l)])
            image_array_prime[:, int(math.ceil(i)), int(j)] = list(image_array[:, int(k), int(l)])
    return np.transpose(image_array_prime)


# Source: https://web.archive.org/web/20150222120106/xenia.media.mit.edu/~cwren/interpolator/
def get_transformation_matrix(points0, points1):
    A = []
    for i in range(0, len(points0)):
        A.append([points1[i][0], points1[i][1], 1, 0, 0, 0, -points0[i][0]*points1[i][0], -points0[i][0]*points1[i][1]])
        A.append([0, 0, 0, points1[i][0], points1[i][1], 1, -points0[i][1]*points1[i][0], -points0[i][1]*points1[i][1]])

    A = np.array(A, dtype=np.float)
    B = np.array(points0).reshape(8, 1)
    lamb = np.dot(np.dot(np.linalg.inv(np.dot(np.transpose(A), A)), np.transpose(A)), B)
    # lamb = np.array(lamb).tolist()
    # lamb.append([1])
    lamb = np.array(lamb).tolist()
    lamb.append([1])

    return np.array(lamb, dtype=np.float).reshape(3, 3)


img0 = Image.open('book2.jpg')
img1 = Image.open('book1.jpg')

img_arr = np.array(img0)

width1, height1 = img1.size
# width0, height0 = img0.size
T = get_transformation_matrix([(318, 256), (534, 372), (316, 670), (73, 473)], [(141, 131), (480, 159), (493, 630), (64, 601)])

new_im_arr = affine_transform(np.transpose(img_arr), T)
new_im = Image.fromarray(new_im_arr.astype('uint8'))
new_im.show()