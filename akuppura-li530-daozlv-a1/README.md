# Assignment1

In this assignment, we will utilize tecchniques we have 
learned from Module 1 to Module 5. Our grade.py program
will proceed as below steps: 

1. Grayscale the image
2. Filter image to reduce high frequency noise
3. Apply Sobel operator to intially find edges 
4. Non-max suppression to reduce duplicate detections
5. Canny to finalize our edge pixels and make binary image
6. Hough transformation to identify segment question blokcs 
and choice blocks. 

We also devise inject.py and extract.py functions to 
embed ground truth to answer sheets.

# 1. Image Filters
In this program, we mainly use two filters. 
## 1.1 Gaussian Filter With Fourier Speed-Up
First of all, the approximate gaussian filter is used to 
remove high frequency patterns. Then, we use Sobel Operator 
to detect both vertical and horizontal edges.

During our experiment, we find that filtering/convolution
is very slow (about 8-15 min) to run with naive implementation.
Luckily, after having studied Module 5, we refactor our implementation
to Fourier transformation which brings in a significant spped-up. 

We have also noticed a very 
important observation that these filters will not remove 
ink from the answer sheet. This helps a lot in the following 
steps regarding reading students' choices correctly 
from answer sheet.

## 1.2 Sobel Operator
We also use a popular 3*3 sobel patch to perform
Sobel operation in order to identify pixels of both
vertical and horizontal edges


# 2. Edge Detection 
In the Detector.py file, we essentially implement 
the canny detector to perform edge detection. The sobel filter from Filter.py and 
non_max_suppression from Detector.py are mainly used to support
our canny detector. 

Our implementation follows the steps in the
slides provided by Professor Crandall, 
1. Filter image with derivative of Gaussian (Gaudssian Filter)
2. Find magnitude and orientation of gradient (Sobel Filter)
3. Non-maximum suppression (non_max_suppression)
4. Linking and thresholding (canny_detector)


## 2.1 Non-Max Suppression
In our non_max_suppression function, we calculate 
the edge strength and gradient direction by gradient
magnitude. Then non-maximum suppression is performed in
four directions (vertical, horizontal, diag and anti-diag). 
Finally, we implement two thredholding in our canny_detector. 


## 2.2 Canny Detector
In the canny_detector, we also perform binarization so all 
marked edge pixels are 1 and the rest is 0. Therefore,
we can just muliply 255 when converting back to image. 


## 2.3 Hough Transformation
After having used canny detector, we also developed functions  
for Hough Tranformation.  We use 2-d array (accumulator) to discretize
the hough space with theta for x-axis and rho for y-axis.

Our implementation includes two important ideas:

1. **Reduce the dimension of hough space:**

    The early hough transformation ran very slow. Since we maintained a 
the accumulator with dimension as (1700, 180). Later, I observed that
our task only requires identification to vertical and horizontal lines. 
Then I just reduced the dimension of theta axis to (1700*2) which 
significantly boost our speed.

2. **Differentiate Threshold For Vertical 
and Horizontal Lines Respectievly:**

    During my experiment, I found that when setting the pixel count
    threshold to around 400, it works perfect on vertical lines, but it 
    will ignore horizontal lines. When setting to around 200, it works 
    well on horizontal lines, but it will create a ton of meaningless
    vertical lines. 
    
    I found that the reason behind this observation results from the 
    difference of boxes count between two directions. For the horizontal
    perspective, we will only have 3*5=15 aligned boxes, and for vertical 
    perspective, we will have 29 boxes. Then the number of 
    votes cast to vertical and horizontal lines differ a lot. 
    
    So in our solution, we simply use two different threshold for
    the two scenarios. After a lot of parameter tuning, we identify
    that about 450 works good for vertical lines and 200 works 
    well for horizontal lines.

 


# 3. Segmentation (Daozhen)
## 3.1 Locate questions based on edges
One approach we use is to locate questions and choice boxes based on edges 
(The hough_grader function in Detector.py). 
However, this solution has some problems.   
The effectiveness of edge detection is not stable. 

    It is hard to find a universal
well-performed parameters for edge detection functions. 
Our current edge detection 
parameters works pretty well for situations like a-3 

    For this problem we only have 
2/85 missed, but for  a-27 34/85 questions missed.  

We can basically get the answer from this method but the due to its unstable, 
we sometimes didn't recognize the line we need to scan. So, we consider more satble way 
for segmentation.

## 3.2 Hardcode question positions
Our hardcode solution origin_grader(based on gray graph) and naive_grader(based on edged graph) works better and more stable.  This two graders simply aggregte pixel values from the area of interest to determine whether there is ink blob.  

However, our naive_grader has some error because it suffers the problem that some ink blob pixels are removed by
edge detectors which then confuse the final vote accumulator.

Initially we run graders directly on the image output from canny detector. 
But that produced crazy errors when we run b-13. After that, we noticed a lot of ink pixels are removed by edge detectors, then we change our implementation. Now our graders 
use two image. A canny image to identify lines of interest, then we go back to
the grayscale image at the same coordinates to count pixels. This change gave us
a significant performance boost up. 

Our guess is that this grader program scenario is pretty well bounded. All answer sheet
are scanned into A4 size image. Then the coordinate location of each question is well
predictable. And our pixel voting approah is actually robust even if the entire answer
sheet shift a little bit since the ink blob will cast a way much higher vote to
the boxes marked by student. Even a partial scan can assure we detect the right answer.

The problem of this method is it sometime can determine if the student want to keep the answer. We scanned the left area of each question, and determine if we need a "x " by 
accumulator of black and white pixels in that area.
Since the small difference among images and noises, we need to adjust the value of z of three grader in Detector.py file to determin whether to put a "x" in the answer or not

# 4. Embedding Barcode (Ashok)
To cover the objective of injecting and retrieving the answers to/from the form, we have selected Barcodes. The space to print the barcode is the unused white space above the shading area.

## 4.1 Our implementation follows the below steps

1. Create a standardised list of CHOICES and mark the correct ones with white color and the other with black color pixel
2. Each question is mapped to column of pixels, with rows indicating the choices
3. Print the pixel and read it from the image as part of the extraction

## 4.2 Observation

**a. Pixel quality loss for JPEG images**

If we assign one pixel for one choice, after we convert it to JPEG, some pixel information gets deformed/lost and the results are inaccurate. Also, it is difficult to validate.

**Fix** : To prevent this issue, we started mutiplying(np.kron - with a factor of 8) the list matrix with a dummy matrix, this helped to increase the pixel density of a particular choice and increased the read accuracy from 76% to 98%.

**b. Predictable barcodes**

After trying the barcode for multiple answer sheets, we identified that the pixel placement(based on choices) is consistent for same answersheets, it mean students can easily able to predict the answers by comparing with other
students.

**Fix** :To prevent this, we have devised an SECRET dispersion function, to disperse the choices randomly for the same answers. For each execution, the dispersion function, generate random positions and the pixels will be placed in different location even for same answersheet. Also, the dispersion will be inversed in the extraction module.

**c. Inconsistencies in Answersheet**

The Groudtruthsheet's answer don't have consistent delimiters, some have question number before the answers, some don't, we have written a reading function which can auto correct these anomalies.



# 5. Running Examples
Let's use a-3 for example:
```
cd akuppura-li530-daozlv-a
grade.py ./test-images/a-3.jpg ./output-files/a-3_segmented.jpg ./output-files/a-3_output.txt
diff -y --suppress-common-lines output-files/output3.txt test-images/a-3_groundtruth.txt | wc -l

python inject.py test-images/a-3.jpg test-images/a-3_groundtruth.txt output-files/a-3_injected.jpg
python extract.py output-files/a-3_injected.jpg output-files/a-3_extracted.txt
```

# 6. Summary

Now, our journey comes to an interesting situation. Even though we tried a lot of 
interesting techniques we have learned from class, 
using our hardcode grader directly on 
grayscale image seems to give the best results. 

We also try the hardcode grader to the edged pictures 
with canny detector, unfortunately, it increases the error rate. 
But as we discussed above, it is understandable, edge detectors and filters 
in fact reduce some ink pixels
in chosen boxes which lower the total vote to the answers students have chosen.

We also try modified hardcode grader a little bit to use detected lines to locate
questions and choices. Sometimes like a-3, it works very well, but sometimes when detectors may
fail to detect edges or over-detect edges, the error rate will go crazy. The problem here
as we stated above is that it is impossible to find a universal parameter to let
our edge detectors work perfect in all scenarios. In the future, we might try some
elastic parameter tuning methods to accomondate this problem.

Another future work we might do to improve this project is to try OCR techniques
to recognize handwirtting characters for the questions where students changed their mind.
Our current solution has successfully identify the location of such scenarios. Next step
is to recenter the character and recognize it maybe with a Convolutional Neuro Network.

Error: (original)
a-3 1/85
a-27 6/85
a-48 3/85
b-13 28/85
