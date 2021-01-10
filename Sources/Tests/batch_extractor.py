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
    CVAlgorithm = CVModule()
    imageTrain = ImageTrain(cache_path)
    image_search = ImageSearch(cache_path)         
    image_count = image_search.get_count()
    image_search.unload()
    ims = ImsES(Elasticsearch())
    try:        
        result = {}
        files = [os.path.join(images_path, p)
                for p in sorted(os.listdir(images_path))]        
        for f in files:               
            img = CVAlgorithm.path_to_image(f)
            kps,des = CVAlgorithm.extract_feature(img)
            result_table = image_search.search_batch(des)       
            if len(result_table) == 0:
                keypoint_serialize = [{'angle': k.angle, 'response': k.response,'octave':k.octave,'class_id':k.class_id,'pt':k.pt,'size':k.size} for k in kps]
                # Append data to already dataset
                new_record = {'id': image_count,
                                'metadata': f,
                                'des': des.flatten(),
                                'kps':keypoint_serialize}
                ims.insert_single_record(new_record, refresh_after=True)
                print(f"{f} train successed")
                image_count += 1
            else:
                print(f"{f} train failed")

        # Loading already dataset
        already_dataset = ims.search_all_record()

        # Trainning it!
        for key in already_dataset:
            imageTrain.addMarkerDes(key["_source"]["id"],key["_source"]["des"])

        # We need the del cache db when out image trainer generator was failed
        if imageTrain.generateMarkerDB() == False:
            print(len(ims.search_all_record()))
            os.remove(cache_path)
        else:
            print("Finised Batch extract")
    except BaseException as e:
        # We need the del cache db when out image trainer generator was failed
        print(f"Error:{e}")
        print(len(ims.search_all_record()))
        if os.path.exists(cache_path):
            os.remove(cache_path)
        pass

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
            kps,des = CVAlgorithm.extract_feature(img)
            result_table,good = image_search.search_batch(des)       
            if len(result_table) == 0:
                keypoint_serialize = [{'angle': k.angle, 'response': k.response,'octave':k.octave,'class_id':k.class_id,'pt':k.pt,'size':k.size} for k in kps]
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


# batch_extractor_form_url()



if __name__ == "__main__":   
    batch_extractor_form_file("../Tests/Batch/")
    # batch_extractor_form_url()
    