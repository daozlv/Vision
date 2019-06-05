from PIL import Image
import numpy as np
import math
import sys


def affine_transform(image_array, transformation_matrix):
    value, width, height = image_array.shape
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
    # Normalizes/Align the coordinates of the transformed pixel locations so that no pixel will be out of bounds.
    height_prime = int(row_max - row_min) + 2
    width_prime = int(col_max - col_min) + 2
    image_list_prime = image_list_prime - np.array([col_min, row_min, 0, 0])
    image_array_prime = np.zeros((3, width_prime, height_prime))

    # Impute pixel values into new image array with some form of "splatting" to fill in black pixels.
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


im = Image.open(sys.argv[1])
im_arr = np.array(im)
Tp = np.array([[0.907, 0.258, -182], [-0.153, 1.44, 58], [-0.000306, 0.000731, 1]])
new_im_arr = affine_transform(np.transpose(im_arr), Tp)
new_im = Image.fromarray(new_im_arr.astype('uint8'))
new_im.show()
