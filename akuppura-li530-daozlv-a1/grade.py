from PIL import Image, ImageOps
import argparse
from PIL import Image, ImageOps
from Filter import Filter
from Detector import Detector
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_im")
    parser.add_argument("output_im")
    parser.add_argument("output_txt")
    args = parser.parse_args()

    print("Recognizing answer sheets....")

    # load image into gray scale
    image = Image.open(args.input_im).convert('RGB')
    image_gray = ImageOps.grayscale(image)

    # convert image to numpy array
    Filter = Filter()
    Detector = Detector()
    array = np.array(image_gray)

    # 1. gaussian blur to remove high frequency noise
    array = Filter.gaussian_filter(array)
    # Image.fromarray(np.uint8(array)*255, 'L').show()

    # 2. apply sobel operator to find gradient
    SobelX, SobelY = Filter.sobel_filter(array)
    # Image.fromarray(np.uint8(SobelX)*255, 'L').show()

    # 3. non-max supprssion
    suppressed = Detector.non_max_suppression((SobelX, SobelY))
    # Image.fromarray(np.uint8(suppressed), 'L').show()

    # 4. canny detection
    canny = Detector.canny_detector(np.uint8(suppressed)*255)
    canny_image = Image.fromarray(np.uint8(canny) * 255, 'L').convert("RGB")
    # Image.fromarray(np.uint8(canny) * 255, 'L').show()

    # 5. Hough transformation
    vertical_lines = Detector.hough_lines(canny, 180, 452)
    horizontal_lines = Detector.hough_lines(canny, 90, 193)

    # output image
    Detector.drawLines(canny_image, vertical_lines[0], vertical_lines[1])
    Detector.drawLines(canny_image, horizontal_lines[0], horizontal_lines[1])
    canny_image.save(args.output_im)
    canny_gray = ImageOps.grayscale(canny_image)
    canny_gray.save(args.output_im)

    ##canny_img = np.uint8(canny_image)#canny_image.load()
    ##find blue line

    # 6. output detected answers to txt file
    answers = Detector.naive_grader(np.uint8(canny) * 255)
    #answers = Detector.origin_grader(np.uint8(image_gray))
    #answers = Detector.hough_grader(np.uint8(canny_gray))

    ##use edged graph to find location will sometimes cause the missing lines

    with open(args.output_txt, "w") as f:
        for i in range(0, 85):###len(answers) if we use hough
            f.write("%d %s\n"%((i + 1), answers[i]))




