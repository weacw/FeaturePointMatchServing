from image_search import ImageSearch
from cvmodule import CVModule
from flask_restful import Resource, reqparse

from elasticsearch_driver import ImsES
from elasticsearch import Elasticsearch
from image_train import ImageTrain


class Image_Del_API(Resource):
    def __init__(self):
        self.ims = ImsES(Elasticsearch())

    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('image_url')
        args = parse.parse_args()

        CVAlgorithm = CVModule()
        img = CVAlgorithm.url_to_image(args['image_url'])
        des = CVAlgorithm.extract_feature(img)

        # Init and load search algorithm
        image_search = ImageSearch("cache/index.db")
        result_table = image_search.search_batch(des)
        image_search.unload()
        print(
            f'current already dataset length:{len( self.ims.search_all_record())}')

        if len(result_table) > 0:
            # Remove the record from already dataset
            print(self.ims.delete_siginle_record({'id': result_table['id']}))

            # Loading already dataset
            already_dataset = self.ims.search_all_record()
            # Re-trainning it!
            self.imageTrain = ImageTrain()
            print(len(already_dataset))
            for key in already_dataset:
                self.imageTrain.addMarkerDes(key["_source"]["des"])
           
            # Rebuild index
            if self.imageTrain.generateMarkerDB('cache/index.db'):
                return {'msg': 'success'}
            else:
                return {'msg': 'eror!'}
        return {'msg': 'there are not math image'}, 202
