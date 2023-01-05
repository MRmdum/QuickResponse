import requests
import base64
from bs4 import BeautifulSoup
from PIL import Image
import PIL

import os
import numpy as np
import pyboof as pb
import cv2

#https://stackoverflow.com/questions/27233351/how-to-decode-a-qr-code-image-in-preferably-pure-python
#class from stackoverflow for pyboof lib
class QR_Extractor:
    # Src: github.com/lessthanoptimal/PyBoof/blob/master/examples/qrcode_detect.py
    def __init__(self):
        self.detector = pb.FactoryFiducial(np.uint8).qrcode()
    
    def extract(self, img_path):
        if not os.path.isfile(img_path):
            print('File not found:', img_path)
            return None
        image = pb.load_single_band(img_path, np.uint8)
        self.detector.detect(image)
        qr_codes = []
        for qr in self.detector.detections:
            qr_codes.append({
                'text': qr.message,
                'points': qr.bounds.convert_tuple()
            })
        return qr_codes

mySession = requests.Session()

##connection to web page

url = "http://challenge01.root-me.org/programmation/ch7/"
page = mySession.get(url)

#parsing
soup = BeautifulSoup(page.content,"html.parser")
results = soup.find_all('img')[0].attrs['src'].split(",")[1]

#decoding base 64 + download
with open("imageToSave.png", "wb") as fh:
    fh.write(base64.decodebytes(results.encode('utf-8')))


#adding squares in qr's corners#
cropingValue = (18,18,282,282)

im = Image.open('imageToSave.png')
im.crop(cropingValue).save('imageToSave.png')
im = Image.open('imageToSave.png')

size = (29,29)
im = im.resize(size)
im.save('imageToSave.png')

pixelMap = im.load()

img = Image.new( im.mode, im.size)
pixelsNew = img.load()
for i in range(img.size[0]):
    for j in range(img.size[1]):
        if pixelMap[i,j][0] >= 100 or pixelMap[i,j][1] >= 100 or pixelMap[i,j][2] >= 100: 
            pixelsNew[i,j] = (255,255,255)
for i in range(img.size[0]):
    for j in range(img.size[1]):
        if i<7 and j<7:
            pixelsNew[i,j] = (0,0,0)
            pixelsNew[img.size[0]-i-1,j] = (0,0,0)
            pixelsNew[i,img.size[1]-j-1] = (0,0,0)
        if i>=1 and i<6 and j>=1 and j<6:
            pixelsNew[i,j] = (255,255,255)
            pixelsNew[img.size[0]-i-1,j] = (255,255,255)
            pixelsNew[i,img.size[1]-j-1] = (255,255,255)
        if i>=2 and i<5 and j>=2 and j<5:
            pixelsNew[i,j] = (0,0,0)
            pixelsNew[img.size[0]-i-1,j] = (0,0,0)
            pixelsNew[i,img.size[1]-j-1] = (0,0,0)

img2 = Image.new("RGB", (33, 33), (255, 255, 255))
pixelsFinal = img2.load()
for i in range(img.size[0]):
    for j in range(img.size[1]):
        pixelsFinal[i+2,j+2]=pixelsNew[i,j]

img2.save('imageToSave.png')

size = (261,261)
img = img2.resize(size,PIL.Image.NEAREST)
img.save('imageToSave.png')
### 

qr_scanner = QR_Extractor()
text = qr_scanner.extract('imageToSave.png')[0]['text']
text = text.removeprefix('The key is ')
print(text)

###

post_params = {'metu' : text}
headers = {'Content-Type' : 'application/x-www-form-urlencoded'}
cookies ={'PHPSESSID': mySession.cookies.get('PHPSESSID')}

rcontent = mySession.post(url,data=post_params,cookies =cookies)

soup = BeautifulSoup(rcontent.content,"html.parser")
results = str(soup.find_all('p')[0])
print(results)

#flag: 