from flask import request, current_app, send_from_directory
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import settings as json_settings
from base64 import b64encode
from json import loads as jsonloads
from os.path import isfile

import hashlib

class FileAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('type', type = str, required = False, default = 'static')
        self.reqparse.add_argument('name', type = str, required = True)
        super(FileAPI, self).__init__()

    def get(self):
        # Return expected parameter output, also set indent settings
        if not request.args:
            return self.create_param_string(), 200

        if (not current_app.debug) and (json_settings and json_settings['indent']):
            json_settings['indent'] = None

        args   = self.reqparse.parse_args()
        if args['type'] == 'static':
            with open('%s/%s' % (current_app.config['STATIC_DIR'], args['name'])) as file:
                str = jsonloads(file.read())
            return str, 200
        elif args['type'] == 'cam':
            if isfile("/lamp/cams/%s/images/M.jpg" % args['name']):
                image = "/lamp/cams/%s/images/M.jpg" % args['name']
            elif isfile("/lamp/cams/%s/images/PAN.jpg" % args['name']):
                image = "/lamp/cams/%s/images/PAN.jpg" % args['name']
            with open(image, "rb") as file:
                str = b64encode(file.read())
            return { 'img': str }, 200
        elif args['type'] == 'hash':
            blocksize = 65536
            hasher = hashlib.sha1()
            with open('%s/%s' % (current_app.config['STATIC_DIR'], args['name'])) as file:
                buf = file.read(blocksize)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = file.read(blocksize)
            return { 'hash': hasher.hexdigest() }, 200
        elif args['type'] == 'logs':
            with open('%s/%s' % (current_app.config['UPLOADS_DIR'], args['name'])) as file:
                str = b64encode(file.read())
            return { 'file': str }, 200

    @staticmethod
    def create_param_string():
        if not current_app.debug:
            json_settings['indent']    = 4
            json_settings['sort_keys'] = True

        params = {}
        params['type'] = { 'type': 'string', 'required': 'no', 'options': 'static, hash, img, cam',
                         'note': 'What type of file to return.'}
        params['name'] = { 'type': 'string', 'required': 'yes', 'note': 'Name of file to return'}
        return params
