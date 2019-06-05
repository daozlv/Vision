import sys
import cv2
import numpy as np
from matplotlib import pyplot as plt


def groupMatrix(disMatrix,k):
   groups = []
   for i in range (len(disMatrix)):
      groups.append([i])
   while ((len(groups))>k):
      maxx = 0
      temp = [0,0]
      for i in range(len(disMatrix)):
         for j in range(i,len(disMatrix)):
            if(disMatrix[i][j]> maxx):
               maxx = disMatrix[i][j]
               temp = [i,j]
               disMatrix[i][j] = 0
      for i in range(len(groups)):
         if temp[0] in groups[i]:
            part1 = groups.pop(i)
            break
      for i in range(len(groups)):
         if temp[1] in groups[i]:
            part2 = groups.pop(i)
            break
      groups.append(part1+part2)
   return groups

   
def compare(filename1, filename2):
   img1 = cv2.imread(filename1, cv2.IMREAD_GRAYSCALE)
   img2 = cv2.imread(filename2, cv2.IMREAD_GRAYSCALE)
   orb = cv2.ORB_create(nfeatures=1000)

   (keypoints1, descriptors1) = orb.detectAndCompute(img1, None)
   (keypoints2, descriptors2) = orb.detectAndCompute(img2, None)

   matches = []
   for i in range(0, len(keypoints1)):
      temp = []
      for j in range(0, len(keypoints2)):
         dis = cv2.norm( descriptors1[i], descriptors2[j], cv2.NORM_HAMMING)
         if dis < 55:
            temp.append([dis,i,j])
      if len(temp)>=2:
         sorted(temp,key=lambda l:l[0])
         matches.append([temp[0][1],temp[0][2]])
         matches.append([temp[1][1],temp[1][2]])
      elif len(temp) == 1:
         matches.append([temp[0][1],temp[0][2]])
   return len(matches)
   ##img3 = drawMatches(img1,keypoints1,img2,keypoints2,matches)
   ##cv2.imwrite("matches.jpg", img3)

def compareknn(filename1, filename2):
   img1 = cv2.imread(filename1, cv2.IMREAD_GRAYSCALE)
   img2 = cv2.imread(filename2, cv2.IMREAD_GRAYSCALE)
   orb = cv2.ORB_create(nfeatures=1000)

   (keypoints1, descriptors1) = orb.detectAndCompute(img1, None)
   (keypoints2, descriptors2) = orb.detectAndCompute(img2, None)

   bf = cv.BFMatcher()
   matches = bf.knnMatch(descriptors1,descriptors2, k=2)
    ##find the close matches points
   good = []
   for m,n in matches:
      if m.distance < 0.75*n.distance:
         good.append(m)
   return len(good)

def drawMatches(img1, kp1, img2, kp2, matches):
   ##use to compare two image with line
   rows1 = img1.shape[0]
   cols1 = img1.shape[1]
   rows2 = img2.shape[0]
   cols2 = img2.shape[1]

   out = np.zeros((max([rows1,rows2]),cols1+cols2,3), dtype='uint8')
   out[:rows1,:cols1] = np.dstack([img1])
   out[:rows2,cols1:] = np.dstack([img2])
   for mat in matches:
      img1_idx = mat[0]
      img2_idx = mat[1]
      (x1,y1) = kp1[img1_idx].pt
      (x2,y2) = kp2[img2_idx].pt
      cv2.circle(out, (int(x1),int(y1)), 4, (255, 0, 0, 1), 1)   
      cv2.circle(out, (int(x2)+cols1,int(y2)), 4, (255, 0, 0, 1), 1)
      cv2.line(out, (int(x1),int(y1)), (int(x2)+cols1,int(y2)), (255, 0, 0, 1), 1)
   return out

k = int(sys.argv[1])
numberOfImg = len(sys.argv)-2
disMatrix = [[0]*numberOfImg for _ in range(numberOfImg)]
for i in range (numberOfImg):
   for j in range(i+1, numberOfImg):
      disMatrix[i][j] = compare(sys.argv[i+2], sys.argv[j+2])
      #disMatrix[i][j] = compareknn(sys.argv[i+2], sys.argv[j+2])
print(disMatrix)
groups = groupMatrix(disMatrix,k)
for i,item in groups:
   for pic in item:
      print(sys.argv[pic+2],end = " ")
   print()
