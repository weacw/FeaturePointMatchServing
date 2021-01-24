import cv2
import base64
import urllib.request
import numpy as np

cv2.useOptimized()
sift = cv2.SIFT_create(nfeatures=100)
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=20)
search_params = dict(checks=150)
flann = cv2.FlannBasedMatcher(index_params, search_params)


class CVModule():

    def __init__(self):
        """
        初始化Opencv
        @sift：sift全名为Scale-invariant feature transform，尺度不变特征转换是一种机器视觉的算法用来侦测与描述影像中的局部性特征，
        它在空间尺度中寻找极值点，并提取出其位置、尺度、旋转不变数，此算法由David Lowe 在1999年所发表，2004年完善总结。
        @FlannBasedMatcher：Fast Library forApproximate Nearest Neighbors
        """
        pass

    
    def read_base64(self, base64Image):
        """
        将Base64转为图片
        @base64Image: base64编码字符串
        """
        npimg = np.frombuffer(base64.b64decode(base64Image), dtype=np.uint8)
        img = cv2.imdecode(npimg, 2)

        # Enhanced gray
        img = np.uint8(np.clip((2 * (np.int16(img)-60) - 225), 0, 255))
        return img

    
    def url_to_image(self, url):
        """
        通过URL下载图片
        @url:网络图片地址
        """
        resp = urllib.request.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, 0)
        return image

    
    def path_to_image(self, path):
        return cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    
    def bytes_to_image(self, bytes):
        image = np.asarray(bytearray(bytes.read()), dtype="uint8")
        if image is None:
            return None
        return cv2.imdecode(image, 0)
    
    def extract_feature(self, img, shape=(400, 400)):
        """
        抽出图像的描述子
        @img:需要抽出描述子的图像
        """
        img = cv2.resize(img, dsize=shape, interpolation=cv2.INTER_LINEAR)
        kps, des = sift.detectAndCompute(img, None)
        return kps, des

    def crop_center(self, img, dim=[800, 800]):
        """
        将图片进行裁剪
        @img:需裁剪的图片
        @dim:裁剪的目标尺寸
        """
        
        if img.shape == dim or img.shape == (512,512) or img.shape == (800,800):
            return img
        img = cv2.resize(img, dsize=(int(img.shape[1]/2),int(img.shape[0]/2)), interpolation=cv2.INTER_LINEAR)
        # cv2.imwrite('resize.jpg',img)

        width, height = img.shape[1], img.shape[0]
        crop_width = dim[0] if dim[0] < img.shape[1] else img.shape[1]
        crop_height = dim[1] if dim[1] < img.shape[0] else img.shape[0]
        mid_x, mid_y = int(width/2), int(height/2.3)
        cw2, ch2 = int(crop_width/2), int(crop_height/2)      
        crop_img = img[mid_y-ch2:mid_y+ch2, mid_x-cw2:mid_x+cw2]
        # cv2.imwrite('croped.jpg',crop_img)
        return crop_img
    
    def match(self, des1, des2):
        """
        将两个描述子进行匹配
        @des1:匹配描述子
        @des2:匹配描述子
        """
        matches = flann.knnMatch(des1, des2, k=2)
        matches = matches[:100]
        good = []

        for m in matches:
            if len(m) == 2:
                if m[0].distance < 0.75 * m[1].distance:
                    good.append(m[0])
        return good

    
    def findHomgraphy(self, good, kps1, kps2):
        """使用RANSAC计算inliner匹配点
        Args:
            good ([match]): [两张图象的匹配特征好点]
            kps1 ([keypoint]): [图像1的关键特侦点]
            kps2 ([keypoint]): [图像2的关键特侦点]

        Returns:
            [float]: [置信度]]
        """

        try:
            src_pts = np.float32(
                [kps1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([kps2[m.trainIdx]['pt']
                                  for m in good]).reshape(-1, 1, 2)
            m, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            correct_matched_kp = [good[i] for i in range(len(good)) if mask[i]]
            percent = len(correct_matched_kp)/len(mask)
            return percent
        except Exception as e:
            print(f"findHomgraphy:{e}")

        return 0

    
    def convetKeypointToDict(self, kps):
        return [{'angle': k.angle, 'response': k.response, 'octave': k.octave, 'class_id': k.class_id, 'pt': k.pt, 'size': k.size} for k in kps]
