from ImageMatch.Restful import *


def merge_dicts(dict1, dict2):
    dict3 = dict1.copy()
    dict3.update(dict2)
    return dict3


class Image_Predict_API(Resource):
    def __init__(self):
        parse = reqparse.RequestParser()
        parse.add_argument('image_url')
        parse.add_argument('image_base64')
        parse.add_argument(
            'image', type=werkzeug.datastructures.FileStorage, location='files')
        parse.add_argument('metadata')
        self.args = parse.parse_args()

    def post(self):
        try:
            img = get_image(CVAlgorithm, self.args)
            img = CVAlgorithm.crop_center(img, dim=dim_800x800)
            kps, des = CVAlgorithm.extract_feature(img)
            image_search = ImageSearch(annoy_index_db_path)
            result_table = image_search.search_batch(des, kps)
            if result_table != None:
                return result_table, 200
        except Exception as BaseException:
            print(BaseException)
            pass

        return {'data': '', 'message': 'Can not found!'}, 200
