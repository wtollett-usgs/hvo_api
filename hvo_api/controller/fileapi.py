# -*- coding: utf-8 -*-
from flask import request, current_app as app
from flask_restful import Resource, reqparse
from base64 import b64encode
from json import loads as jsonloads
from os.path import isfile

import hashlib


class FileAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('type', type=str, required=False,
                                   default='static')
        self.reqparse.add_argument('name', type=str, required=True)
        super(FileAPI, self).__init__()

    def get(self):
        # Return expected parameter output, also set indent settings
        if not request.args:
            return self.create_param_string(), 200

        if not app.debug:
            app.config['RESTFUL_JSON'] = {}

        args = self.reqparse.parse_args()
        if args['type'] == 'static':
            with open(f"{app.config['STATIC_DIR']}/{args['name']}") as file:
                str = jsonloads(file.read())
            return str, 200
        elif args['type'] == 'cam':
            if isfile("/lamp/cams/%s/images/M.jpg" % args['name']):
                image = "/lamp/cams/%s/images/M.jpg" % args['name']
            elif isfile("/lamp/cams/%s/images/PAN.jpg" % args['name']):
                image = "/lamp/cams/%s/images/PAN.jpg" % args['name']
            with open(image, "rb") as file:
                str = b64encode(file.read()).decode('utf-8')
            info  = "/lamp/cams/%s/images/js.js" % args['name']
            with open(info, 'r') as file:
                line = file.readline()
                date = line.split('"')[1]
            return {'img': str, 'date': date}, 200
        elif args['type'] == 'hash':
            blocksize = 65536
            hasher = hashlib.sha1()
            with open(f"{app.config['STATIC_DIR']}/{args['name']}") as file:
                buf = file.read(blocksize)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = file.read(blocksize)
            return {'hash': hasher.hexdigest()}, 200

    @staticmethod
    def create_param_string():
        if not app.debug:
            settings = app.config.get('RESTFUL_JSON', {})
            settings.setdefault('indent', 4)
            settings.setdefault('sort_keys', True)
            app.config['RESTFUL_JSON'] = settings

        params = {}
        params['type'] = {'type': 'string', 'required': 'no',
                          'options': 'static, hash, img, cam',
                          'note': 'What type of file to return.'}
        params['name'] = {'type': 'string', 'required': 'yes',
                          'note': 'Name of file to return'}
        return params
