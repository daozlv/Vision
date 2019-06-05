import numpy as np
import cv2
from matplotlib import pyplot as plt
import sys
if __name__ == '__main__':
    img1 = cv2.imread(sys.argv[1])
    img2 = cv2.imread(sys.argv[2])
    #expand img size for putting two img together
    srcImg = cv2.copyMakeBorder(img1, 200, 200, 0, 800, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    testImg = cv2.copyMakeBorder(img2, 200, 200, 0, 800, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    img1gray = cv2.cvtColor(srcImg, cv2.COLOR_BGR2GRAY)
    img2gray = cv2.cvtColor(testImg, cv2.COLOR_BGR2GRAY)
    
    orb = cv2.ORB_create(nfeatures=1000)
    (keypoints1, descriptors1) = orb.detectAndCompute(img1gray, None)
    (keypoints2, descriptors2) = orb.detectAndCompute(img2gray, None)
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(descriptors1,descriptors2, k=2)
    ##find the close matches points
    good = []
    for m,n in matches:
        if m.distance < 0.75*n.distance:
            good.append(m)
            
    MIN_MATCH_COUNT = 10
    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        warpImg = cv2.warpPerspective(testImg, np.array(M), (testImg.shape[1], testImg.shape[0]), flags=cv2.WARP_INVERSE_MAP)
        cv2.imwrite("warpImg.jpg", warpImg)
        ##setup empty img
        res = np.zeros([srcImg.shape[0], srcImg.shape[1], 3], np.uint8)
        for row in range(0, srcImg.shape[0]):
            for col in range(0, srcImg.shape[1]):
                ##directly use origin img if there is pixel in the output img
                if not srcImg[row, col].any():
                    res[row, col] = warpImg[row, col]
                elif not warpImg[row, col].any():
                    res[row, col] = srcImg[row, col]
                else:
                    res[row, col] = np.clip(srcImg[row, col]/2 + warpImg[row, col]/2, 0, 255)

        cv2.imwrite(sys.argv[3], res)
    else:
        print("Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT))
        matchesMask = None
