from gevent import monkey
monkey.patch_all()
import os
from flask import Flask
from flask_restful import Api
from ImageMatch.Restful.predict_api import Image_Predict_API
from ImageMatch.Restful.del_image_api import Image_Del_API
from ImageMatch.Restful.train_api import Image_Train_API
from gevent.pywsgi import WSGIServer

monkey.patch_all()
if not os.path.exists("cache"):
    os.makedirs("cache")

app = Flask(__name__)
api = Api(app)
api.add_resource(Image_Train_API, '/v1/add_image')
# api.add_resource(Image_Del_API, '/v1/del_image')
api.add_resource(Image_Predict_API, '/v1/predict_image')


if __name__ == "__main__":
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
    # app.run()
