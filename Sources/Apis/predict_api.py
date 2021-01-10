import base64
import json
from image_search import ImageSearch
from cvmodule import CVModule
from flask_restful import Resource, reqparse


from elasticsearch_driver import ImsES
from elasticsearch import Elasticsearch
import werkzeug


class Image_Predict_API(Resource):
    def __init__(self):
        self.ims = ImsES(Elasticsearch())
        self.CVAlgorithm = CVModule()
        self.image_search = ImageSearch("cache/index.db")


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


    def post(self):
        try:
            img = self.get_image()            
            kps,des = self.CVAlgorithm.extract_feature(img)
            result_table = self.image_search.search_batch(des)    
            result_ids_table = list()
            [result_ids_table.append(result['id'])  for result in result_table]
            records = self.ims.search_multiple_record(result_ids_table)
            records_index =0 

            # Check the result length, when the result length is greater than 0, get the matching data            
            for result in result_table:
                # record = self.ims.search_single_record({'id': result['id']})
                record = records[records_index]["_source"]
                RANSAC_percent = self.CVAlgorithm.findHomgraphy(result['good'],kps,record['kps'])
                records_index+=1
                if len(record) > 0 and RANSAC_percent>0.5:
                    # Remove the field of des. Because the des field is storing the image description data and self.CVAlgorithm.findHomgraphy(good,kps,record['kps'])
                    result.pop('good')
                    record.pop('des')
                    record.pop('kps')
                    result['confidence']=RANSAC_percent
                    result = self.merge_dicts(result,record)
                    return result, 200
        except Exception as BaseException:
            print(BaseException)
            pass

        return {'data': '', 'message': 'Can not found!'}, 200

    def merge_dicts(self, dict1, dict2):
        dict3 = dict1.copy()
        dict3.update(dict2)
        return dict3
