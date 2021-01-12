from image_search import ImageSearch
from image_train import ImageTrain
from cvmodule import CVModule
from flask_restful import Resource, reqparse

from elasticsearch_driver import ImsES
from elasticsearch import Elasticsearch
from Utitliy import get_image,timer
from configure_runtime  import *

class Image_Train_API(Resource):
    def __init__(self):
        self.ims = ImsES(Elasticsearch())
        self.CVAlgorithm = CVModule()
        self.image_search = ImageSearch(annoy_index_db_path)
        self.imageTrain = ImageTrain(annoy_index_db_path)

    @timer
    def post(self):
        img, self.args = get_image(self.CVAlgorithm)     
        img = self.CVAlgorithm.crop_center(img, dim=[800, 800])
        if img.shape != (800,800):
            return {'msg': 'Image size is not enough'}, 200 
        kps,des = self.CVAlgorithm.extract_feature(img)

        # Init and load search algorithm
        result_table = self.image_search.search_batch(des)
        image_count = self.image_search.get_count()
        self.image_search.unload()                

        if des is  None:            
            return {'msg': 'Image description is not enough'}, 200  

        # Annoy index no data found
        if len(result_table) == 0:
            return self.build_record(image_count,kps,des)

        # Annoy index data found, We also need to match the data one by one        
        for data in result_table:                        
            record = self.ims.search_single_record({'id':data['id']})
            RANSAC_percent = self.CVAlgorithm.findHomgraphy(data['good'], kps, record['kps'])

            # If it finds any very similar data, it will jump out of the test directly
            if RANSAC_percent > 0.5:                
                return {'data':'', 'msg': 'there are already image'}, 202
            
        return self.build_record(image_count,kps,des)


    def build_record(self,image_count,kps,des):
        keypoint_serialize = [{'angle': k.angle, 'response': k.response,'octave':k.octave,'class_id':k.class_id,'pt':k.pt,'size':k.size} for k in kps]

        metadata = self.args['metadata']
        if metadata is None:
            metadata = self.args['image'].filename
        

        # Append data to already dataset
        new_record = {'id': image_count,
                    'metadata':metadata,
                    'des': des.flatten(),
                    'kps': keypoint_serialize}
        self.ims.insert_single_record(new_record, refresh_after=True)

        # Loading already dataset
        already_dataset = self.ims.search_all_record()

        # Trainning it!
        for key in already_dataset:
            self.imageTrain.addMarkerDes(key["_source"]["id"],key["_source"]["des"])

        # Rebuild index
        if self.imageTrain.generateMarkerDB():
            return {'msg': 'success'}      