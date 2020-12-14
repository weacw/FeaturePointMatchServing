import base64
import json
from image_search import ImageSearch
from cvmodule import CVModule
from flask_restful import Resource, reqparse


from elasticsearch_driver import ImsES
from elasticsearch import Elasticsearch


class Image_Predict_API(Resource):
    def __init__(self):
        self.ims = ImsES(Elasticsearch())

    def post(self):
        # Parse http data
        parse = reqparse.RequestParser()
        parse.add_argument('image_url')
        args = parse.parse_args()

        # Start matching
        CVAlgorithm = CVModule()
        img = CVAlgorithm.url_to_image(args['image_url'])
        crop_predict_img = CVAlgorithm.crop_center(
            img, int(img.shape[0]*0.8), int(img.shape[0]*0.8))
        kp, des = CVAlgorithm.extract_feature(crop_predict_img)

        # Init and load search algorithm
        image_search = ImageSearch("cache/index.db")
        result_table = image_search.search_batch(des)

        # Check the result length, when the result length is greater than 0, get the matching data
        if len(result_table) > 0:
            record = self.ims.search_single_record({'id': result_table['id']})
            if len(record) > 0:

                # Remove the field of des. Because the des field is storing the image description data
                record.pop('des')

                # merge dict for client
                result_table = self.merge_dicts(record, result_table)
                return result_table, 200
        return {'data': '', 'message': 'Can not found!'}, 200

    def merge_dicts(self, dict1, dict2):
        dict3 = dict1.copy()
        dict3.update(dict2)
        return dict3
