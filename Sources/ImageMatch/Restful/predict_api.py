from ImageMatch.Restful import *

class Image_Predict_API(Resource):
    def __init__(self):
        self.args = create_args()
        

    def post(self):
        """图像验证Restful API        

        Returns:
            [json]: [查询反馈，若查询到数据则反馈为该图像的数据]
            Successed:
            {
                "id": 1,
                "metadata": "../Tests/Benchmark\\bq01.jpg",
                "timestamp": "2021-01-21T14:53:51.047920",
                "matchscore": 100
            }

            Failed:
            {
                'data':'',
                'message':'Can not found!'
            }
        """
        try:
            img = get_image(CVAlgorithm, self.args)
            img = CVAlgorithm.crop_center(img, dim=(512,512))
            kps, des = CVAlgorithm.extract_feature(img)

            image_search = ImageSearch(annoy_index_db_path)
            result_table = image_search.search_batch(des, kps)            
            
            if result_table != None:
                return result_table, 200            
        except Exception as BaseException:
            print(BaseException)

        return {'data': '', 'message': 'Can not found!'}, 200
