from image_search import ImageSearch
from cvmodule import CVModule
from flask_restful import Resource

from elasticsearch_driver import ImsES
from elasticsearch import Elasticsearch
from image_train import ImageTrain
from Utitliy import get_image
from configure_runtime import *


class Image_Del_API(Resource):
    def __init__(self):
        self.ims = ImsES(Elasticsearch())
        self.CVAlgorithm = CVModule()
        # Init by configure_runtime.py
        self.db_path = annoy_index_db_path
        self.image_search = ImageSearch(self.db_path)
        self.imageTrain = ImageTrain(self.db_path)

    def delete(self):
        img, self.args = get_image(self.CVAlgorithm)
        img = self.CVAlgorithm.crop_center(img, dim=[800, 800])
        kps, des = self.CVAlgorithm.extract_feature(img)

        # Init and load search algorithm

        result_table = self.image_search.search_batch(des)
        self.image_search.unload()

        # Collection  the id fields
        result_ids_table = list()
        [result_ids_table.append(result['id']) for result in result_table]
        records = self.ims.search_multiple_record(result_ids_table)     

        # Annoy index data found, We also need to match the data one by one
        for data_index in range(len(result_table)):
            record = records[data_index]["_source"]
            data = result_table[data_index]
            RANSAC_percent = self.CVAlgorithm.findHomgraphy(data['good'], kps, record['kps'])
            
            # If it finds any very similar data, it will jump out of the test directly
            if RANSAC_percent >= 0.5:
                self.ims.delete_siginle_record({'id': record['id']})

                # Loading already dataset and rebuild it!
                already_dataset = self.ims.search_all_record()
                for key in already_dataset:
                    self.imageTrain.addMarkerDes(key["_source"]["id"], key["_source"]["des"])

                 # Rebuild index
                if self.imageTrain.generateMarkerDB():
                    return {'msg': success_response}
                else:
                    return {'msg': 'eror!'}
        return {'msg': already_img_response}, 202
