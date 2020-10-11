import os
import cv2
import base64
import pickle
import werkzeug
import numpy as np
from flask import Flask
from image_search import ImageSearch
from image_train import ImageTrain
from cvmodule import CVModule
from flask_restful import Resource, Api, reqparse




class Image_Train_API(Resource):
    def __init__(self):
        self.CVModule = CVModule()

    def get(self):
        label_db = open('cache/label_db.pickle', 'rb')
        labels = pickle.load(label_db)
        print(len(labels))

        for n in labels:
            print(n)

    def post(self):

        self.image_search = ImageSearch("cache/test.db")
        parse = reqparse.RequestParser()
        # , type=werkzeug.datastructures.FileStorage, location='files')
        parse.add_argument('image_url')
        parse.add_argument('metadata')
        args = parse.parse_args()
        # img_url = self.CVModule.read_base64(args['image_url'])
        
        img = self.CVModule.url_to_image(args['image_url'])
        kp, des = self.CVModule.extract_feature(img)
        result_table = self.image_search.search_batch(des)
        self.image_search.unload()

        if len(result_table) == 0:
            dat_name = 'cache/des_db.pickle'
            label_name = 'cache/label_db.pickle'

            des_dict = dict()
            label_list = []

            if os.path.exists(dat_name):
                if os.path.getsize(dat_name) > 0:
                    with open(dat_name, 'rb') as dat:
                        unpickler = pickle.Unpickler(dat)
                        des_dict = unpickler.load()

            if os.path.exists(label_name):
                if os.path.getsize(label_name) > 0:
                    with open(label_name, 'rb') as labels_db:
                        label_list = pickle.load(labels_db)

            with open(dat_name, 'wb') as des_db:
                if args['metadata'] not in des_dict:
                    des_dict[args['metadata']] = des.flatten()
                    pickle.dump(des_dict, des_db)

            self.imageTrain = ImageTrain()
            for key in des_dict:
                print(des_dict[key])
                self.imageTrain.addMarkerDes(des_dict[key])
                if key not in label_list:
                    label_list.append(key)

            if self.imageTrain.generateMarkerDB('cache/test.db'):
                with open(label_name,'wb') as labels_db:
                    pickle.dump(label_list, labels_db)
                return {'msg': 'success'}
        return {'msg': 'there are already image'}

    def delete(self):
        pass


# class Http_Server():
#     def __init__(self):
#         #Create folder to cache marker data
#         if not os.path.exists("cache"):
#             os.makedirs("cache")

#         self.app = Flask(__name__)
#         self.api = Api(self.app)
#         self.api.add_resource(Image_Train_API, '/v1/add_image')

#     def run(self):
#         self.app.run(debug=True)



# if "__main__":
#     http_server = Http_Server()
#     http_server.run()


if not os.path.exists("cache"):
    os.makedirs("cache")

app = Flask(__name__)
api = Api(app)
api.add_resource(Image_Train_API, '/v1/add_image')