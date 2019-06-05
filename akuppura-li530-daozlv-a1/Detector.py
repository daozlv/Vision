from PIL import Image, ImageDraw, ImageFilter
import copy
import numpy as np


class Detector(object):

    def __init__(self):
        pass


    def non_max_suppression(self, gradients):
        ''' Perform non-max suppression on gradients image
        :param
            gradients: tuple containing gradients on x and y direction
        :return:
            res: an image as numpy array
        '''
        image_grad = np.power(np.power(gradients[0], 2) + np.power(gradients[1], 2), .5)	# edge strength
        theta = np.arctan2(gradients[1], gradients[0])									# gradient direction
        thetaQ = (np.round(theta * (5.0 / np.pi)) + 5) % 5  						    # Quantize direction

        #res = np.zeros(image_grad.shape)
        res = image_grad.copy()
        n, m = gradients[0].shape
        for i in range(n):
            for j in range(m):
                # ignore image bound
                if i == 0 or i == n-1 or j == 0 or j == m - 1:
                    res[i, j] = 0
                    continue

                angle = thetaQ[i, j] % 4

                if angle == 0:  # horizontal
                    if image_grad[i, j] <= image_grad[i, j - 1] or image_grad[i, j] <= image_grad[i, j + 1]:
                        res[i, j] = 0
                if angle == 1:  # diag
                    if image_grad[i, j] <= image_grad[i - 1, j + 1] or image_grad[i, j] <= image_grad[i + 1, j - 1]:
                        res[i, j] = 0
                if angle == 2:  # vertical
                    if image_grad[i, j] <= image_grad[i - 1, j] or image_grad[i, j] <= image_grad[i + 1, j]:
                        res[i, j] = 0
                if angle == 3:  # anti-diag
                    if image_grad[i, j] <= image_grad[i - 1, j - 1] or image_grad[i, j] <= image_grad[i + 1, j + 1]:
                        res[i, j] = 0
        return res


    def canny_detector(self, gradients, thresholds = (10, 20)):
        lowThreshold = thresholds[0]
        highThreshold = thresholds[1]
        n, m = gradients.shape

        # categorize pixels:
        # >highThreshold 2
        # >lowThreshold 1
        # else 0
        res = np.array(gradients>highThreshold, dtype=np.uint8)
        sub = []
        allPixels = np.array(res, dtype=np.uint8) + np.array(gradients>lowThreshold, dtype=np.uint8)
        for r in range(1, n-1):
            for c in range(1, m-1):
                if allPixels[r, c] != 1:
                    continue

                # check neighbors
                local = allPixels[r - 1:r + 2, c - 1:c + 2]
                localmax = local.max()
                if localmax == 2:
                    sub.append((r, c))
                    res[r, c] = 1

        # Recursively extend edges
        while len(sub) > 0:
            tmp = []
            for r, c in sub:
                for a in range(-1, 2):
                    for b in range(-1, 2):
                        if a != 0 or b != 0:
                            r2 = r + a
                            c2 = c + b
                            # connect this pixel to result
                            if allPixels[r2, c2] == 1 and res[r2, c2] == 0:
                                tmp.append((r2, c2))
                                res[r2, c2] = 1
            sub = tmp
        return res


    def naive_grader(self, image):
        ''' Naively hardcode question block, and identify answers by accumulating pixel brightness
        :param
            image: numpy array
        :return:
            answers: array of final answers
        '''
        answers = []
        answer = [[0 for i in range(360)] for j in range(28)]
        weights = []    # high weight indicates ink blob
        for col in range(3):
            for row in range(29):
                a = b = c = d = e = z = 0
                for i in range(28):
                    for j in range(360):
                        answer[i][j] = int(image[i + 674 + 48 * row, j + 200 + 430 * col])
                        if (j < 60):
                            z += int(image[i + 674 + 48 * row, j + 200 + 430 * col])
                        if (60 < j < 120):
                            a += int(image[i + 674 + 48 * row, j + 200 + 430 * col])
                        if (120 < j < 180):
                            b += int(image[i + 674 + 48 * row, j + 200 + 430 * col])
                        if (180 < j < 240):
                            c += int(image[i + 674 + 48 * row, j + 200 + 430 * col])
                        if (240 < j < 300):
                            d += int(image[i + 674 + 48 * row, j + 200 + 430 * col])
                        if (300 < j < 360):
                            e += int(image[i + 674 + 48 * row, j + 200 + 430 * col])
                # print(question)
                weights.append([a, b, c, d, e, z])
                sol = ""
                if (a > 70000 or (a > b and a > c and a > d and a > e)):
                    sol += "A"
                if (b > 70000 or (b > a and b > c and b > d and b > e)):
                    sol += "B"
                if (c > 70000 or (c > a and c > b and c > d and c > e)):
                    sol += "C"
                if (d > 70000 or (d > a and d > b and d > c and d > e)):
                    sol += "D"
                if (e > 70000 or (e > a and e > b and e > c and e > d)):
                    sol += "E"
                ##no stable based on different img input Need to adjust
                if z > 70000:
                    sol += " x "
                answers.append(sol)
        # print(questions)
        return answers

    def hough_grader(self,canny):
        ''' Grader based on hough
        :param
            image: numpy array
        :return:
            answers: array of final answers
        '''
        answers = []
        answer = [[0 for i in range(360)] for j in range(28)]
        weights = []    # high weight indicates ink blob
        row =670
        colblock=[[],[],[]]##3questions per block of row
        while row < 2100:
            if (canny[row,0]!=0):
                col = 0
                k=0##index of colblock
                while col < 1200:
                    if (canny[0,col]!= 0):
                        a = b = c = d = e = z = 0
                        for i in range(28):
                            for j in range(360):
                                ##canny[row+i,col+j-60] = 255
                                ##img[col+j-60, row+i] = 0
                                if (j < 60):
                                    z += int(canny[row+i,col+j-60])
                                if (60 < j < 120):
                                    a += int(canny[row+i,col+j-60])
                                if (120 < j < 180):
                                    b += int(canny[row+i,col+j-60])
                                if (180 < j < 240):
                                    c += int(canny[row+i,col+j-60])
                                if (240 < j < 300):
                                    d += int(canny[row+i,col+j-60])
                                if (300 < j < 360):
                                    e += int(canny[row+i,col+j-60])
                        sol = ""
                        if (a > 70000 or (a > b and a > c and a > d and a > e)):
                            sol += "A"
                        if (b > 70000 or (b > a and b > c and b > d and b > e)):
                            sol += "B"
                        if (c > 70000 or (c > a and c > b and c > d and c > e)):
                            sol += "C"
                        if (d > 70000 or (d > a and d > b and d > c and d > e)):
                            sol += "D"
                        if (e > 70000 or (e > a and e > b and e > c and e > d)):
                            sol += "E"
                        ##no stable based on different img input Need to adjust
                        if z > 70000:
                            sol += " x "
                        colblock[k].append(sol)
                        k+=1
                        col+=400
                    col+=1
                row += 40####adjustable size until next block avoiding noise
            row+=1
        answers=colblock[0]+colblock[1]+colblock[2]
        return answers

    def origin_grader(self, image):
        ''' Grader based on origin scanned graph
        :param
            image: numpy array
        :return:
            answers: array of final answers
        '''
        answers = []
        answer = [[0 for i in range(360)] for j in range(28)]
        weights = []    # high weight indicates ink blob

        for col in range(3):
            for row in range(29):
                a = b = c = d = e = z = 0
                for i in range(28):
                    for j in range(360):
                        answer[i][j] = int(image[i + 674 + 48 * row, j + 200 + 430 * col])
                        if (j < 60):
                            z += int(image[i + 674 + 48 * row, j + 200 + 430 * col])
                        if (60 < j < 120):
                            a += int(image[i + 674 + 48 * row, j + 200 + 430 * col])
                        if (120 < j < 180):
                            b += int(image[i + 674 + 48 * row, j + 200 + 430 * col])
                        if (180 < j < 240):
                            c += int(image[i + 674 + 48 * row, j + 200 + 430 * col])
                        if (240 < j < 300):
                            d += int(image[i + 674 + 48 * row, j + 200 + 430 * col])
                        if (300 < j < 360):
                            e += int(image[i + 674 + 48 * row, j + 200 + 430 * col])
                # print(question)
                weights.append([a, b, c, d, e, z])
                sol = ""
                if (a < 310000 or (a < b and a < c and a < d and a < e)):
                    sol += "A"
                if (b < 310000 or (b < a and b < c and b < d and b < e)):
                    sol += "B"
                if (c < 310000 or (c < a and c < b and c < d and c < e)):
                    sol += "C"
                if (d < 310000 or (d < a and d < b and d < c and d < e)):
                    sol += "D"
                if (e < 310000 or (e < a and e < b and e < c and e < d)):
                    sol += "E"

                ##no stable based on different img input Need to adjust
                if z < 330000:
                    sol += " x "
                #sol += str([a, b, c, d, e, z])
                if sol != "":
                    answers.append(sol)
        # print(questions)
        return answers



    def hough_lines(self, image, theta, threshold=400):
        ''' Transform image to hough space with polar coord
        :param:
            image: numpy array indicating line pixels
            theta: desired angle of lines
        :return:
            thetas: theta coords
            rhos:   rho coords
        '''

        height, width = image.shape
        max_len = int(np.sqrt(width**2 + height**2))+1   # diag line is longest straight line in image

        # discretize theta and rho so we can store as 2-d array
        thetas = np.linspace(theta-180, theta, 2)*np.pi/180
        rhos = np.linspace(-height, height, height*2)
        res_thetas = []
        res_rhos = []

        cos = np.cos(thetas)
        sin = np.sin(thetas)

        # 2-d accumulator array (theta, rho) to record vote
        accumulator = np.zeros((len(rhos), len(thetas)), dtype=np.uint64)
        y_coords, x_coords = np.nonzero(image)

        # Vote in the hough accumulator
        for i in range(len(x_coords)):
            x = x_coords[i]
            y = y_coords[i]

            for t_idx in range(len(thetas)):
                rho = int(x*cos[t_idx] + y*sin[t_idx]) + height
                if abs(rho)>=height:
                    continue
                accumulator[rho, t_idx] += 1

                if accumulator[rho, t_idx]==threshold:    # record valid line
                    res_thetas.append(thetas[t_idx])
                    res_rhos.append(rhos[rho])

        return (res_thetas, res_rhos)


    def drawLines(self, image, thetas, rhos):
        ''' Translate points in hough space back to lines
        :param
            image: PIL image object, need to be drawn by ImageDraw
            thetas: theta coords
            rhos:   rho coords
        :return:
            null
        '''
        draw = ImageDraw.Draw(image)
        width, height = image.size
        n = len(thetas)
        for i in range(n):
            rho = rhos[i]
            theta = thetas[i]
            a = np.cos(theta)
            b = np.sin(theta)
            if b==0:    # sin(theta)==0, vertical line
                draw.line((rho/a, 0, rho/a, height-1), fill=(0,0,255), width=3)
            elif a==0:  # horizontal line
                draw.line((0, rho, width-1, rho), fill=(0,0,255), width=3)
            else:
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 2*width * (-b))
                y1 = int(y0 + 2*height * (a))
                x2 = int(x0 - 2*width * (-b))
                y2 = int(y0 - 2*height * (a))

                draw.line(xy=(x1, y1, x2, y2), fill=(0,0,255,0), width=3)
        return





