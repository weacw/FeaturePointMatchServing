from ImageMatch.Restful  import *

def merge_dicts(dict1, dict2):
    dict3 = dict1.copy()
    dict3.update(dict2)
    return dict3
    

class Image_Predict_API(Resource):
    def __init__(self):
        pass

    def post(self):
        try:
            img, args =  get_image(CVAlgorithm)
            img = CVAlgorithm.crop_center(img, dim=dim_800x800)
            kps, des = CVAlgorithm.extract_feature(img)        
            result_table = image_search.search_batch(des)                   
            # Collection  the id fields
            # result_ids_table = list()
            # [result_ids_table.append(result['id']) for result in result_table]
            # records = ims.search_multiple_record(result_ids_table)            
            # Check the result length, when the result length is greater than 0, get the matching data
            for data_index in result_table:                
                data = data_index
                RANSAC_percent = CVAlgorithm.findHomgraphy(data['good'], kps, data['kps'])
                if  RANSAC_percent > 0.5:
                    # Remove the field of des. Because the des field is storing the image description data
                    data.pop('des')
                    data.pop('kps')
                    data.pop('good')
                    data['confidence'] = RANSAC_percent
                    # data = merge_dicts(data, record)
                    return data, 200
        except Exception as BaseException:
            print(BaseException)
            pass

        return {'data': '', 'message': 'Can not found!'}, 200

