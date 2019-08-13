#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import numpy
import pyautogui
import time
from collections import defaultdict
import cv2
from scipy.misc import imsave

try:
    from PIL import Image
    import PIL.ImageOps
except ImportError:
    import Image
import pytesseract
# TODO replace with your path
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Abrar\AppData\Local\Tesseract-OCR\tesseract.exe"


expedition_logs = defaultdict(list)


def parse_screenshot(text, page):
    """Get text info from OCR and convert into dictionary form in logs."""
    rows = text.split("\n")
    for row in rows:
        entry = row.split()
        name_end = len(entry) - 5
        user = []
        for ind in range(name_end):
            user.append(entry[ind].strip())
        user = " ".join(user)
        user.strip()
        user = safe_str(user)

        if user == "":
            continue

        expedition_logs[user] = []

        for level, column in enumerate(entry):
            if level < name_end:
                continue

            column = column.strip()
            ind = column.find("(")
            try:
                expeditions_done = int(column[:ind])
            except ValueError:
                expeditions_done = 0
            expedition_logs[user].append(expeditions_done)

        expedition_logs[user].append(page)


def sum_expeditions(expeditions):
    result = 0
    for ind, value in enumerate(expeditions):
        if ind == 5:
            break
        if value == "":
            value = 0
        result += (ind + 1) * int(value)
    return result


def safe_str(obj):
    try:
        return str(obj)
    except UnicodeEncodeError:
        return obj.encode('ascii', 'ignore').decode('ascii')
    return ""


def get_parser():
    """Get parser object for script """
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--clean",
                        dest="clean_option",
                        help="image cleaning option",
                        choices=["invert", "binarize", "cv2"],
                        type=str,
                        required=True)
    parser.add_argument("--threshold",
                        dest="threshold",
                        default=180,
                        type=int,
                        help="Threshold when to show white")
    parser.add_argument("--resize",
                        dest="resize",
                        default=3,
                        type=int,
                        help="Amount of times to resize the image")
    """
    parser.add_argument("-o", "--output",
                        dest="output",
                        help="write binarized file hre",
                        metavar="FILE",
                        required=True)
    """
    return parser


def binarize_image(img_path, threshold):
    """Binarize an image."""
    image_file = Image.open(img_path)
    image = image_file.convert('L')  # convert image to monochrome
    image = numpy.array(image)
    image = binarize_array(image, threshold)
    imsave(img_path, image)


def binarize_array(numpy_array, threshold=200):
    """Binarize a numpy array."""
    for i in range(len(numpy_array)):
        for j in range(len(numpy_array[0])):
            if numpy_array[i][j] > threshold:
                numpy_array[i][j] = 255
            else:
                numpy_array[i][j] = 0
    return numpy_array


def remove_green(image):
    image = image.convert('RGBA')
    data = numpy.array(image)
    # just use the rgb values for comparison
    rgb = data[:, :, :3]
    color = [72, 72, 72]   # Original value
    background = [19, 19, 19, 255]
    mask = numpy.all(rgb == color, axis=-1)
    # change all pixels that match color to background color
    data[mask] = background
    return Image.fromarray(data)


if __name__ == "__main__":
    time.sleep(2)
    args = get_parser().parse_args()

    # TODO: might need to change this 8, depends on how many scrolls you need
    # need to scroll around 8 times down to parse through the entire alliance list
    for ind in range(0, 8):

        # last scroll has drag-back by the in-game menu
        if ind == 7:
            time.sleep(3)

        output = "screenshots/%d.png" % (ind)

        # get expedition screen from the  middle and improve contrast / invert colors
        # TODO replace with your coordinates
        image = pyautogui.screenshot(region=(550, 354, 964, 552))
        width, height = image.size

        if args.clean_option == "invert":
            image = image.resize((args.resize*width, args.resize*height))
            image = PIL.ImageOps.invert(image)
            image.save(output)
        elif args.clean_option == "binarize":
            image = image.resize((args.resize*width, args.resize*height))
            binarize_image(output, args.threshold)
            image = Image.open(output)
        elif args.clean_option == "cv2":
            image.save(output)
            image = cv2.imread(output)
            image = cv2.bitwise_not(image)
            image = cv2.resize(image, None, fx=1.5, fy=1.7,
                               interpolation=cv2.INTER_CUBIC)  # scale
            cv2.imwrite(output, image)

        text = pytesseract.image_to_string(
            image, config='--psm 6')

        parse_screenshot(text, ind)

        # TODO: change this in accordance with above todo
        if ind == 7:
            break

        # TODO: need your own computer coordinates
        pyautogui.moveTo(1493, 876, duration=0.25)
        pyautogui.drag(0, -463, button='left', duration=1)

    row_data = []
    # condense into row of |user|1|2|3|4|5|total|
    for user, expeditions in expedition_logs.items():
        row_data.append([])
        row_data[-1].append(user)

        for expedition in expeditions:
            row_data[-1].append(safe_str(expedition))

        total_points = sum_expeditions(expeditions)
        row_data[-1].append(total_points)

    # sort by decreasing total score, descending order
    row_data.sort(key=lambda x: x[-1], reverse=True)
    for ind, line in enumerate(row_data):
        pass
    for line in row_data:
        print(line)
    print(len(row_data))

    with open("result.csv", "wb") as result_file:
        writer = csv.writer(result_file)
        writer.writerows(row_data)
