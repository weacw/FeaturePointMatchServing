import numpy as np
import cv2
import os
from flask_restful import Resource, reqparse
import sys
sys.path.append("..")
from elasticsearch import Elasticsearch
from elasticsearch_driver import ImsES
from cvmodule import CVModule
from image_train import ImageTrain
from image_search import ImageSearch
import argparse
import requests

cache_path ='../cache/index.db'


urls = [
    "https://www.gxar.com/gsl/1.jpg",
    "https://www.gxar.com/gsl/2.jpg",
    "https://www.gxar.com/gsl/3.jpg",
    "https://www.gxar.com/gsl/4.jpg",
    "https://www.gxar.com/gsl/5.jpg",
    "https://www.gxar.com/gsl/6.jpg",
    "https://www.gxar.com/gsl/7.jpg",
    "https://www.gxar.com/gsl/8.jpg",
    "https://www.gxar.com/gsl/9.jpg",
    "https://www.gxar.com/gsl/10.jpg",
    "https://www.gxar.com/gsl/11.jpg",
    "https://www.gxar.com/gsl/12.jpg",
    "https://www.gxar.com/gsl/13.jpg",
    "https://www.gxar.com/gsl/14.jpg",
    "https://www.gxar.com/gsl/15.jpg",
    "https://www.gxar.com/tts/1.jpg",
    "https://www.gxar.com/tts/2.jpg",
    "https://www.gxar.com/tts/3.jpg",
    "https://www.gxar.com/tu/01.jpg",
    "https://www.gxar.com/tu/02.jpg",
    "https://www.gxar.com/tu/03.jpg",
    "https://www.gxar.com/tu/04.jpg",
    "https://www.gxar.com/tu/05.jpg",
    "https://www.gxar.com/tu/06.jpg",
    "https://www.gxar.com/tu/1.jpg",
    "https://www.gxar.com/tu/2.jpg",
    "https://www.gxar.com/tu/3.jpg",
    "https://www.gxar.com/tu/4.jpg",
    "https://www.gxar.com/tu/5.jpg"
]


class batch_tools():
    def __init__(self):
        self.gateway = 'http://127.0.0.1:5000/v1/add_image'
    
    def startTrain(self, images_path):
        files = [os.path.join(images_path, p) for p in sorted(os.listdir(images_path))]
        for f in files:
            with open(f, 'rb') as img:
                trainImg = {'image': img}
                response = requests.post(self.gateway,data={'metadata':f}, files=trainImg)
                print(f"file:{f},Response:{response.text}")

if __name__ == "__main__":
    batch = batch_tools()
    batch.startTrain('../Tests/Benchmark')