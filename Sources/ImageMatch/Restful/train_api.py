from ImageMatch.Restful import *
from ImageMatch.Cores.image_train import ImageTrain


class Image_Train_API(Resource):
    def __init__(self):
        self.imageTrain = ImageTrain(annoy_index_db_path)
        parse = reqparse.RequestParser()
        parse.add_argument('image_url')
        parse.add_argument('image_base64')
        parse.add_argument(
            'image', type=werkzeug.datastructures.FileStorage, location='files')
        parse.add_argument('metadata')
        self.args = parse.parse_args()

    def post(self):
        img = get_image(CVAlgorithm, self.args)

        if img is None:
            return {'msg': 'Image data error'}, 200

        img = CVAlgorithm.crop_center(img, dim=dim_800x800)

        if img.shape != dim_800x800:
            return {'msg': 'Image size is not enough'}, 200

        kps, des = CVAlgorithm.extract_feature(img)

        # Init and load search algorithm
        image_search = ImageSearch(annoy_index_db_path)
        result_table = image_search.search_batch(des, kps)
        image_count = image_search.get_count()
        image_search.unload()

        if des is None:
            return {'msg': 'Image description is not enough'}, 200

        # Annoy index no data found
        if result_table is None and kps is not None and des is not None:
            return self.build_record(image_count, kps, des)
        else:
            return {'data': '', 'msg': 'there are already image'}, 202

    def build_record(self, image_count, kps, des):
        keypoint_serialize = [{'angle': k.angle, 'response': k.response, 'octave': k.octave,
                               'class_id': k.class_id, 'pt': k.pt, 'size': k.size} for k in kps]

        metadata = self.args['metadata']
        if metadata is None:
            metadata = self.args['image'].filename

        # # Append data to already dataset
        new_record = {'id': image_count,
                      'metadata': metadata,
                      'des': des.flatten(),
                      'kps': keypoint_serialize}
        ims.insert_single_record(new_record, refresh_after=True)

        # Loading already dataset
        already_dataset = ims.search_all_record()

        # # Trainning it!
        for key in already_dataset:
            self.imageTrain.addMarkerDes(
                key["_source"]["id"], key["_source"]["des"])

        # # Rebuild index
        if self.imageTrain.generateMarkerDB():
            return {'msg': 'success'}
