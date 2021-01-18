import base64
import json
from image_search import ImageSearch
from cvmodule import CVModule
from flask_restful import Resource
from elasticsearch_driver import ImsES
from elasticsearch import Elasticsearch
from Utitliy import get_image
from configure_runtime  import *

class Image_Predict_API(Resource):
    def __init__(self):
        self.ims = ImsES(Elasticsearch())
        self.CVAlgorithm = CVModule()
        self.image_search = ImageSearch(annoy_index_db_path)

    def post(self):
        try:
            img, self.args = get_image(self.CVAlgorithm)
            img = self.CVAlgorithm.crop_center(img, dim=dim_800x800)
            kps, des = self.CVAlgorithm.extract_feature(img)        
            result_table = self.image_search.search_batch(des)            
            # Collection  the id fields
            result_ids_table = list()
            [result_ids_table.append(result['id']) for result in result_table]
            records = self.ims.search_multiple_record(result_ids_table)
            # Check the result length, when the result length is greater than 0, get the matching data
            for data_index in range(len(result_table)):
                record = records[data_index]["_source"]
                data = result_table[data_index]
                RANSAC_percent = self.CVAlgorithm.findHomgraphy(
                    data['good'], kps, record['kps'])
                if len(record) > 0 and RANSAC_percent > 0.5:
                    # Remove the field of des. Because the des field is storing the image description data
                    record.pop('des')
                    record.pop('kps')
                    data.pop('good')
                    data['confidence'] = RANSAC_percent
                    data = self.merge_dicts(data, record)
                    return data, 200
        except Exception as BaseException:
            print(BaseException)
            pass

        return {'data': '', 'message': 'Can not found!'}, 200

    def merge_dicts(self, dict1, dict2):
        dict3 = dict1.copy()
        dict3.update(dict2)
        return dict3
