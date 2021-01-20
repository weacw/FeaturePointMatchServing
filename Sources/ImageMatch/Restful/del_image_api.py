from ImageMatch.Restful import *


class Image_Del_API(Resource):
    def __init__(self):
        pass

    def delete(self):
        img, args = get_image(CVAlgorithm)
        img = CVAlgorithm.crop_center(img, dim=dim_800x800)
        kps, des = CVAlgorithm.extract_feature(img)

        # Init and load search algorithm

        result_table = image_search.search_batch(des)
        image_search.unload()

        # Collection  the id fields
        result_ids_table = list()
        [result_ids_table.append(result['id']) for result in result_table]
        records = ims.search_multiple_record(result_ids_table)

        # Annoy index data found, We also need to match the data one by one
        for data_index in range(len(result_table)):
            record = records[data_index]["_source"]
            data = result_table[data_index]
            RANSAC_percent = CVAlgorithm.findHomgraphy(
                data['good'], kps, record['kps'])

            # If it finds any very similar data, it will jump out of the test directly
            if RANSAC_percent >= 0.5:
                ims.delete_siginle_record({'id': record['id']})

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
