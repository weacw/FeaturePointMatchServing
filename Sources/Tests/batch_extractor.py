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


def batch_extractor_form_file(images_path):
    files = [os.path.join(images_path, p)
             for p in sorted(os.listdir(images_path))]
    CVAlgorithm = CVModule()
    image_search = ImageSearch(cache_path)
    result = {}
    for f in files:
        # print 'Extracting features from image %s' % f
        name = f.split('/')[-1].lower()
        kp, des = CVAlgorithm.extract_feature(f)
        result_table = image_search.search_batch(des)
        image_count = image_search.get_count()
        image_search.unload()
        if len(result_table) == 0:
            # Append data to already dataset
            new_record = {'id': image_count,
                          'metadata': self.args['metadata'],
                          'des': des.flatten()}
            self.ims.insert_single_record(new_record, refresh_after=True)

            # Loading already dataset
            already_dataset = self.ims.search_all_record()

            # Trainning it!
            self.imageTrain = ImageTrain()
            for key in already_dataset:
                imageTrain.addMarkerDes(key["_source"]["id"],key["_source"]["des"])

    print("Finised Batch extract")


def batch_extractor_form_url():
    files = urls
    CVAlgorithm = CVModule()
    imageTrain = ImageTrain()
    image_search = ImageSearch(cache_path)
    ims = ImsES(Elasticsearch())
    image_count = image_search.get_count()
    image_search.unload()
    try:     
        for f in files:
            img = CVAlgorithm.url_to_image(f)
            des = CVAlgorithm.extract_feature(img)
            result_table = image_search.search_batch(des)
            if len(result_table) == 0:
                # Append data to already dataset
                new_record = {'id': image_count,
                                'metadata': f,
                                'des': des.flatten()}
                ims.insert_single_record(new_record, refresh_after=True)
                image_count += 1

        # Loading already dataset
        already_dataset = ims.search_all_record()

        # Trainning it!
        for key in already_dataset:
            imageTrain.addMarkerDes(key["_source"]["id"],key["_source"]["des"])

        # We need the del cache db when out image trainer generator was failed
        if imageTrain.generateMarkerDB(cache_path) == False:
            print(len(ims.search_all_record()))
            os.remove(cache_path)
        else:
            print("Finised Batch extract")
    except BaseException as e:
        # We need the del cache db when out image trainer generator was failed
        print(f"Error:{e}")
        print(len(ims.search_all_record()))
        os.remove(cache_path)
        pass


batch_extractor_form_url()
