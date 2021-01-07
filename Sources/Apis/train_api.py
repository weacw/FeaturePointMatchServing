from image_search import ImageSearch
from image_train import ImageTrain
from cvmodule import CVModule
from flask_restful import Resource, reqparse

from elasticsearch_driver import ImsES
from elasticsearch import Elasticsearch
import werkzeug

class Image_Train_API(Resource):
    def __init__(self):
        self.ims = ImsES(Elasticsearch())        
        self.CVAlgorithm = CVModule()

    def get_image(self):
        parse = reqparse.RequestParser()
        parse.add_argument('image_url')        
        parse.add_argument('image_base64')
        parse.add_argument('image', type=werkzeug.datastructures.FileStorage, location='files')
        parse.add_argument('metadata')
        self.args = parse.parse_args()

        if self.args['image_url'] is not None:
            return  self.CVAlgorithm.url_to_image(self.args['image_url'])
        elif self.args['image_base64'] is not None:
            return  self.CVAlgorithm.read_base64(self.args['image_base64'])
        else:
            return  self.CVAlgorithm.bytes_to_image(self.args['image'])             

    def post(self):
        img = self.get_image()
        des = self.CVAlgorithm.extract_feature(img)

        # Init and load search algorithm
        image_search = ImageSearch("cache/index.db")
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
                self.imageTrain.addMarkerDes(key["_source"]["id"],key["_source"]["des"])

            # Rebuild index
            if self.imageTrain.generateMarkerDB('cache/index.db'):
                return {'msg': 'success'}
        return {'data': '', 'msg': 'there are already image'}, 202
