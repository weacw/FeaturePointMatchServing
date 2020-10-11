import os
import cv2
import pickle
import numpy as np
from cvmodule import CVModule
from annoy import AnnoyIndex


class ImageTrain():
    def __init__(self):
        self.cvmodule = CVModule()
        self.desArray = []
       
    def addMarkerDes(self,des):
         self.desArray.append(des)

    def generateMarkerDB(self, db_name):
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
