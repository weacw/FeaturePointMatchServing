import cv2
import base64
import urllib.request
import pickle
import numpy as np


class CVModule():
    """
    初始化Opencv
    @ORB：ORB全名为Oriented FAST and Rotated BRIEF，它采用改进的FAST关键点检测方法，使其具有方向性，并采用具有旋转不变性的BRIEF特征描述子。
    FAST和BRIEF都是非常快速的特征计算方法，因此ORB具有非同一般的性能优势。
    @FlannBasedMatcher：Fast Library forApproximate Nearest Neighbors
    """

    def __init__(self):
        self.orb = cv2.ORB_create()
        index_params = dict(algorithm=6, table_number=12,
                            key_size=12, multi_probe_level=1)
        search_params = dict(checks=150)
        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

    """
    将Base64转为图片
    @base64Image: base64编码字符串
    """

    def read_base64(self, base64Image):
        npimg = np.frombuffer(base64.b64decode(base64Image), dtype=np.uint8)
        return cv2.imdecode(npimg, 0)

    """
    通过URL下载图片
    @url:网络图片地址
    """

    def url_to_image(self, url):
        resp = urllib.request.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, 0)
        return image

    """
    抽出图像的描述子
    @img:需要抽出描述子的图像
    """

    def extract_feature(self, img):
        img = cv2.resize(img, dsize=(800, 800), interpolation=cv2.INTER_AREA)        
        kps = self.orb.detect(img)
        kps = sorted(kps, key=lambda x: -x.response)[:]
        kps, des = self.orb.compute(img, kps)
        return des
        # return self.orb.detectAndCompute(img, None)

    """
    将图片进行裁剪
    @img:需裁剪的图片
    @dim:裁剪的目标尺寸
    """

    def crop_center(self, img, dim=[800, 800]):
        width, height = img.shape[1], img.shape[0]
        crop_width = dim[0] if dim[0] < img.shape[1] else img.shape[1]
        crop_height = dim[1] if dim[1] < img.shape[0] else img.shape[0]
        mid_x, mid_y = int(width/2), int(height/2)
        cw2, ch2 = int(crop_width/2), int(crop_height/2)
        crop_img = img[mid_y-ch2:mid_y+ch2, mid_x-cw2:mid_x+cw2]
        return crop_img

    """
    将两个描述子进行匹配
    @des1:匹配描述子
    @des2:匹配描述子
    """

    def match(self, des1, des2):
        matches = self.flann.knnMatch(des1, des2, k=2)
        good = []
        for i, (m, n) in enumerate(matches):
            if m.distance < 0.8*n.distance:
                good.append([m])
        return good
