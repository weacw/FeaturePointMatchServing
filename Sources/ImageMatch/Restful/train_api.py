import pickle
from ImageMatch.Restful import *
from ImageMatch.Cores.image_train import ImageTrain
from ImageMatch.Cores.Utitliy import *


class Image_Train_API(Resource):
    def __init__(self):
        self.imageTrain = ImageTrain(annoy_index_db_path)


    def post(self):
        img, self.args = get_image(CVAlgorithm)
        img = CVAlgorithm.crop_center(img, dim=dim_800x800)
        if img.shape != dim_800x800:
            return {'msg': 'Image size is not enough'}, 200
        kps, des = CVAlgorithm.extract_feature(img)

        # Init and load search algorithm
        result_table = image_search.search_batch(des)
        image_count = image_search.get_count()
        image_search.unload()
        # print( result_table)

        if des is None:
            return {'msg': 'Image description is not enough'}, 200

        # Annoy index no data found
        if len(result_table) == 0:
            return self.build_record(image_count, kps, des)
        # Annoy index data found, We also need to match the data one by one
        for data in result_table:
            record = ims.search_single_record({'id': data['id']})
            # print( decode_dict_in_list(record['kps']))

            RANSAC_percent = CVAlgorithm.findHomgraphy(
                data['good'], kps, decode_dict_in_list(record['kps']))

            # If it finds any very similar data, it will jump out of the test directly
            if RANSAC_percent > 0.5:
                return {'data': '', 'msg': 'there are already image'}, 202

        return self.build_record(image_count, kps, des)

    def build_record(self, image_count, kps, des):
        keypoint_serialize = [{'angle': k.angle, 'response': k.response, 'octave': k.octave,
                               'class_id': k.class_id, 'pt': k.pt, 'size': k.size} for k in kps]

        metadata = self.args['metadata']
        if metadata is None:
            metadata = self.args['image'].filename

        # Append data to already dataset
        new_record = {'id': image_count,
                      'metadata': metadata,
                      'des': encode_vector(des),
                      'kps': encode_dict_in_list(keypoint_serialize)}
        ims.insert_single_record(new_record)

        # Loading already dataset
        already_dataset = ims.search_all_record()

        # Trainning it!
        for key in already_dataset:
            self.imageTrain.addMarkerDes(key["id"], decode_vector(key["des"]))

        # Rebuild index
        if self.imageTrain.generateMarkerDB():
            return {'msg': 'success'}
