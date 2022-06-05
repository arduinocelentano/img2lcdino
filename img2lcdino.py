#!/usr/bin/python3

# img2lcdino - a simple script to convert images to Arduino code for rendering them on a text-based LCD, like 1602 etc.
# Copyright (C) 2022 arduinocelentano

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import cv2
from glob import glob

# SETTINGS
PIXELS_DIFFERENCE = 0 # 0 - loseless, larger values lead to more aggressive compresion
GLOB = "*.png" # files to process
PAUSE = "  delay(250);" # set correct arduono code for frame delay here, script knows nothing about your fps

# generating the beginning of the sketch
def printPreamble():
    print("#include <LiquidCrystal.h>")
    print("LiquidCrystal lcd(22, 21, 19, 18, 17, 16);\n") ### <- set your LCD pins here
    print("void setup()\n{")
    print("  lcd.begin(16, 2);")
    print("  lcd.setCursor(0,0);")
    print("  lcd.write(byte(0));")
    print("  lcd.write(byte(1));")
    print("  lcd.write(byte(2));")
    print("  lcd.write(byte(3));")
    print("  lcd.setCursor(0,1);")
    print("  lcd.write(byte(4));")
    print("  lcd.write(byte(5));")
    print("  lcd.write(byte(6));")
    print("  lcd.write(byte(7));")
    print("  uint8_t a[] = {B00000,B00000,B00000,B00000,B00000,B00000,B01000,B11000};")

# extract rectangle from image 
# and convert it to a list of strings
# like ["00101", "10001",...] 
# (which is custom character's pixmap)
def extractRect(img,x1,y1,x2,y2):
    rect = []
    for i in range (y1,y2):
        rect.append("")
        for j in range (x1,x2):
            if img[i][j][0]:
                rect[len(rect)-1]+="1"
            else:
                rect[len(rect)-1]+="0"
    return rect

# convert an image to LCD frame
# one LCD frame is eight 5x8 characters
def img2frame(img):
    if len(img)<17 or len(img[0])<23:
        return None
    frame = []
    frame.append(extractRect(img,0,0,5,8))
    frame.append(extractRect(img,6,0,11,8))
    frame.append(extractRect(img,12,0,17,8))
    frame.append(extractRect(img,18,0,23,8))
    frame.append(extractRect(img,0,9,5,17))
    frame.append(extractRect(img,6,9,11,17))
    frame.append(extractRect(img,12,9,17,17))
    frame.append(extractRect(img,18,9,23,17))
    return frame

# compare two character pixmaps
# and return a number of different pixels
def compareChars(c1, c2):
    count = 0
    for i in range(len(c1)):
        for j in range(len(c1[i])):
            if c1[i][j] != c2[i][j]:
                count += 1
    return count

####
#The beginning of main script
###
printPreamble()
changed = 0
total = 0
prevFrame = []
for fn in sorted(glob(GLOB)):
    print("//processing ", fn)
    img = cv2.imread(fn)
    (thresh, bwImg) = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    frame = img2frame(bwImg)
    if len(prevFrame):
        for i in range(0,len(frame)):
            total+=1
            if compareChars(frame[i], prevFrame[i])>PIXELS_DIFFERENCE:
                changed += 1
                for j in range(len(frame[i])):
                    print("  a["+str(j)+"]=B"+frame[i][j]+";")
                print("  lcd.createChar("+str(i)+", a);")
    print(PAUSE)
    prevFrame = frame
print("}")
print("void loop(){}")
print("//Changed:", changed)
print("//Total:", total)
print("//", 100*changed/total, "%")
