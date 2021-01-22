import base64
import json
from ImageMatch.Cores import *
from flask_restful import Resource, reqparse
import werkzeug
from ImageMatch.Cores.Utitliy import timer


def create_args():
    parse = reqparse.RequestParser()
    parse.add_argument('image_url')
    parse.add_argument('image_base64')
    parse.add_argument(
        'image', type=werkzeug.datastructures.FileStorage, location='files')
    parse.add_argument('metadata')
    return parse.parse_args()
