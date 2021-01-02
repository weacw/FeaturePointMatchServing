import os
import cv2
import pickle
import numpy as np
from annoy import AnnoyIndex


class ImageTrain():
    def __init__(self):
        """初始化
        """
        self.desArray = []

    def addMarkerDes(self, des):
        """添加单个识别图数据

        Args:
            des (description): 通过opencv orb展开的图像描述符
        """
        if isinstance(des, np.ndarray) is False:
            des = np.array(des)
        self.desArray.append(des)

    def generateMarkerDB(self, db_name):
        """用于生成追踪数据库

        Args:
            db_name (string): 数据库名称

        Returns:
            Bool: True即为构建数据库成功，反之则为失败
        """

        try:
            f = 16000
            t = AnnoyIndex(f, 'angular')
            for des in self.desArray:
                if des.size < 16000:
                    des = np.concatenate(
                        [des, np.zeros(16000 - des.size)])
                t.add_item(t.get_n_items(), des)
            t.build(20)
            t.save(f"{db_name}")
            return True
        except Exception:
            print(Exception)
            return False
