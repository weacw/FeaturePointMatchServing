from ImageMatch.Restful import *
from ImageMatch.Cores.image_train import ImageTrain
imageTrain = ImageTrain(annoy_index_db_path)


class Image_Train_API(Resource):
    def __init__(self):
        pass

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

        if des is None:
            return {'msg': 'Image description is not enough'}, 200

        # Annoy index no data found
        if len(result_table) == 0:
            return self.build_record(image_count, kps, des)

        # Annoy index data found, We also need to match the data one by one
        for data in result_table:
            record = ims.search_single_record({'id': data['id']})
            RANSAC_percent = CVAlgorithm.findHomgraphy(
                data['good'], kps, record['kps'])

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
                      'des': des.flatten(),
                      'kps': keypoint_serialize}
        ims.insert_single_record(new_record, refresh_after=True)

        # Loading already dataset
        already_dataset = ims.search_all_record()

        # Trainning it!
        for key in already_dataset:
            imageTrain.addMarkerDes(
                key["_source"]["id"], key["_source"]["des"])

        # Rebuild index
        if imageTrain.generateMarkerDB():
            return {'msg': 'success'}
