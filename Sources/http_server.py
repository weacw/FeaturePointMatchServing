import os
from flask import Flask
from flask_restful import  Api

from Apis.predict_api import Image_Predict_API
from Apis.del_image_api import Image_Del_API
from Apis.train_api import Image_Train_API

if not os.path.exists("cache"):
    os.makedirs("cache")

app = Flask(__name__)
api = Api(app)
api.add_resource(Image_Train_API, '/v1/add_image')
api.add_resource(Image_Del_API, '/v1/del_image')
api.add_resource(Image_Predict_API, '/v1/predict_image')


if __name__ == "__main__":
    app.run()
