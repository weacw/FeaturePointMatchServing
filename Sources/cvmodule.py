import cv2
import base64
import urllib.request
import pickle
import numpy as np


class CVModule():
    def __init__(self):
        self.orb = cv2.ORB_create()
        index_params = dict(algorithm=6,
                            table_number=12,
                            key_size=12,
                            multi_probe_level=1)
        search_params = dict(checks=150)
        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

    def read_base64(self, base64Image):
        npimg = np.frombuffer(base64.b64decode(base64Image), dtype=np.uint8)
        return cv2.imdecode(npimg, 0)

    def url_to_image(self,url):
        resp = urllib.request.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, 0)
        return image
    def extract_feature(self, img):
        img = cv2.resize(img, dsize=(800, 800), interpolation=cv2.INTER_AREA)
        return self.orb.detectAndCompute(img, None)

    def crop_center(self, img, cropx, cropy):
        y, x = img.shape
        startx = x//2-(cropx//2)
        starty = y//2-(cropy//2)
        return img[starty:starty+cropy, startx:startx+cropx]


    def match(self, des1, des2):
        matches = self.flann.knnMatch(des1, des2, k=2)
        good = []
        for i, (m, n) in enumerate(matches):
            if m.distance < 0.8*n.distance:
                good.append([m])
        return good

        