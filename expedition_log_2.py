#!/usr/bin/python
# -*- coding: utf-8 -*-
import cv2
import re
from scipy.misc import imsave

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Abrar\AppData\Local\Tesseract-OCR\tesseract.exe"


def parse_screenshot(text):
    """Get text info from OCR and convert into dictionary form in logs."""
    rows = text.split("\n")
    valuesRegex = re.compile(r'([0-9O]*\(\+?[0-9O]+\))')
    valueRegex = re.compile(r'([0-9]+)\(\+?([0-9]+)\)')
    expeditions = {}
    for row in rows:
        values = valuesRegex.findall(row)
        name = row[:row.find(values[0])-1]
        name.strip()
        name = safe_str(name)
        expeditions[name] = []
        for value in values:
            value.replace('O', '0')  # sometimes it confuses 0 with O
            matches = re.search(valueRegex, value)
            total = matches.group(1)
            current = matches.group(2)
            expeditions[name].append((int(total), int(current)))
    return expeditions


def sum_expeditions(expeditions):
    for name in expeditions:
        totalTotal = 0
        totalCurr = 0
        for index, value in enumerate(expeditions[name]):
            totalTotal += (index + 1) * value[0]
            totalCurr += (index + 1) * value[1]
        print(f'{name} -> total points: {totalTotal}, current points: {totalCurr}')


def safe_str(obj):
    try:
        return str(obj)
    except UnicodeEncodeError:
        return obj.encode('ascii', 'ignore').decode('ascii')
    return ""


if __name__ == "__main__":
        # get expedition screen from the  middle and improve contrast / invert colors
    image = cv2.imread("screenshot2.png")
    image = cv2.bitwise_not(image)
    image = cv2.resize(image, None, fx=1.5, fy=1.7,
                       interpolation=cv2.INTER_CUBIC)  # scale
    cv2.imwrite('output.png', image)

    text = pytesseract.image_to_string(
        image, config='--psm 6')
    print(text)
    sum_expeditions(parse_screenshot(text))
