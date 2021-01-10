from image_search import ImageSearch
from cvmodule import CVModule
from flask_restful import Resource, reqparse

from elasticsearch_driver import ImsES
from elasticsearch import Elasticsearch
from image_train import ImageTrain
import werkzeug


class Image_Del_API(Resource):
    def __init__(self):
        self.ims = ImsES(Elasticsearch())
        self.CVAlgorithm = CVModule()
        self.db_path ='cache/index.db'
        self.image_search = ImageSearch(self.db_path)
        self.imageTrain = ImageTrain(self.db_path)

    def delete(self):      
        img = self.get_image()
        kps, des = self.CVAlgorithm.extract_feature(img)

        # Init and load search algorithm
      
        result_table = self.image_search.search_batch(des)
        self.image_search.unload()       

        if len(result_table) > 0:
            # Remove the record from already dataset
            print(self.ims.delete_siginle_record({'id': result_table[0]['id']}))

            # Loading already dataset
            already_dataset = self.ims.search_all_record()

            # Re-trainning it!

            for key in already_dataset:
                self.imageTrain.addMarkerDes(
                    key["_source"]["id"], key["_source"]["des"])

            # Rebuild index
            if self.imageTrain.generateMarkerDB():
                return {'msg': 'success'}
            else:
                return {'msg': 'eror!'}
        return {'msg': 'there are not math image'}, 202

    def get_image(self):
        parse = reqparse.RequestParser()
        parse.add_argument('image_url')        
        parse.add_argument('image_base64')
        parse.add_argument('image', type=werkzeug.datastructures.FileStorage, location='files')
        parse.add_argument('metadata')
        self.args = parse.parse_args()        
        if self.args['image_url'] is not None:
            img = self.CVAlgorithm.url_to_image(self.args['image_url'])
            crop_predict_img = self.CVAlgorithm.crop_center(img,dim=[800,800])
        elif self.args['image'] is not None:                
            img = self.CVAlgorithm.bytes_to_image(self.args['image'])
            crop_predict_img = self.CVAlgorithm.crop_center(img,dim=[800,800])
        else:
            img = self.CVAlgorithm.read_base64(self.args['image_base64'])            
            crop_predict_img = self.CVAlgorithm.crop_center(img)
        return crop_predict_img