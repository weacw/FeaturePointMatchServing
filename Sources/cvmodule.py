import cv2
import base64
import urllib.request
import pickle
import numpy as np


class CVModule():
    """
    初始化Opencv
    @sift：sift全名为Scale-invariant feature transform，尺度不变特征转换是一种机器视觉的算法用来侦测与描述影像中的局部性特征，
    它在空间尺度中寻找极值点，并提取出其位置、尺度、旋转不变数，此算法由David Lowe 在1999年所发表，2004年完善总结。
    @FlannBasedMatcher：Fast Library forApproximate Nearest Neighbors
    """

    def __init__(self):
        self.sift = cv2.SIFT_create(nfeatures=100)
        # index_params = dict(algorithm=6, table_number=12,
        #                     key_size=12, multi_probe_level=1)
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm = FLANN_INDEX_KDTREE,trees = 5)
        search_params = dict(checks=300)
        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

    """
    将Base64转为图片
    @base64Image: base64编码字符串
    """

    def read_base64(self, base64Image):
        npimg = np.frombuffer(base64.b64decode(base64Image), dtype=np.uint8)
        img = cv2.imdecode(npimg, 2)
        # Enhanced gray
        img = np.uint8(
            np.clip((2 * (np.int16(img)-60) -225), 0, 255))
        return img

    """
    通过URL下载图片
    @url:网络图片地址
    """

    def url_to_image(self, url):
        resp = urllib.request.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, 0)
        return image

    def path_to_image(self, path):
        return cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    def bytes_to_image(self, bytes):
        image = np.asarray(bytearray(bytes.read()), dtype="uint8")
        return cv2.imdecode(image, 0)

    """
    抽出图像的描述子
    @img:需要抽出描述子的图像
    """
    def extract_feature(self, img, shape=(800, 800)):
        img = cv2.resize(img, dsize=shape, interpolation=cv2.INTER_NEAREST)
        kps = self.sift.detect(img)
        # kps = sorted(kps, key=lambda x: -x.response)
        kps, des = self.sift.compute(img, kps)
        return kps, des

    """
    将图片进行裁剪
    @img:需裁剪的图片
    @dim:裁剪的目标尺寸
    """

    def crop_center(self, img, dim=[512, 512]):        
        width, height = img.shape[1], img.shape[0]
        crop_width = dim[0] if dim[0] < img.shape[1] else img.shape[1]
        crop_height = dim[1] if dim[1] < img.shape[0] else img.shape[0]
        mid_x, mid_y = int(width/2), int(height/2)
        cw2, ch2 = int(crop_width/2), int(crop_height/2)
        crop_img = img[mid_y-ch2:mid_y+ch2, mid_x-cw2:mid_x+cw2]
        cv2.imwrite('croped.jpg', crop_img)
        return crop_img

    """
    将两个描述子进行匹配
    @des1:匹配描述子
    @des2:匹配描述子
    """

    def match(self, des1, des2):       
        matches = self.flann.knnMatch(des1, des2, k=2)
        good = []
        for m in matches:
            if len(m) == 2:
                if m[0].distance < 0.75 * m[1].distance:
                    good.append(m[0])

        # 弃用，用迭代会引发 ValueError: not enough values to unpack (expected 2, got 1)
        # for i, (m, n) in enumerate(matches):
        #     if len(matches[i]) == 2:
        #         if m.distance < 0.75*n.distance:
        #             good.append([m])
        return good

    def findHomgraphy(self, good, kps1, kps2):
        src_pts = np.float32(
            [kps1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kps2[m.trainIdx]['pt']
                              for m in good]).reshape(-1, 1, 2)
        m, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()

        correct_matched_kp = [good[i] for i in range(len(good)) if mask[i]]
        percent = len(correct_matched_kp)/len(mask)      
        print(f"RANSAC Match length:{percent}")
        return percent
       

    def convetKeypointToDict(self, kps):
        return [{'angle': k.angle, 'response': k.response, 'octave': k.octave, 'class_id': k.class_id, 'pt': k.pt, 'size': k.size} for k in kps]
