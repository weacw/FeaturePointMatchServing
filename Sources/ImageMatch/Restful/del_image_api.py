from ImageMatch.Restful import *
from ImageMatch.Cores.image_train import ImageTrain


class Image_Del_API(Resource):
    def __init__(self):
        self.args = create_args()

    def delete(self):
        img = get_image(CVAlgorithm, self.args)

        if img is None:
            return {'msg': 'Image data error'}, 200

        if img.shape != dim_800x800:
            return {'msg': 'Image size is not enough'}, 200

        kps, des = CVAlgorithm.extract_feature(img)

        # Init and load search algorithm
        image_search = ImageSearch(annoy_index_db_path)
        result_table = image_search.search_batch(des, kps)
        image_search.unload()

        if result_table != None:
            imageTrain = ImageTrain(annoy_index_db_path)
            ims.delete_siginle_record({'id': result_table['id']})
            # Loading already dataset and rebuild it!
            already_dataset = ims.search_all_record()
            for key in already_dataset:
                imageTrain.addMarkerDes(
                    key["_source"]["id"], key["_source"]["des"])

                # Rebuild index
            if imageTrain.generateMarkerDB():
                return {'msg': success_response}
            else:
                return {'msg': 'eror!'}
        return {'msg': already_img_response}, 202