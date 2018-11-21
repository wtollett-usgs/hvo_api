# -*- coding: utf-8 -*-
from .common_constants import SFMT
from base64 import b64encode as be
from datetime import datetime
from flask import request, current_app
from flask_restful import Resource
from html.parser import HTMLParser
from json import loads as jsonload
from logging import getLogger
from requests.auth import HTTPBasicAuth

import os
import pytz
import requests
import traceback


class LogsAPI(Resource):
    def __init__(self):
        super(LogsAPI, self).__init__()

    def get(self):
        if not current_app.debug:
            current_app.config['RESTFUL_JSON'] = {}

        url = f"{os.getenv('LOGS_BASE')}api/getposts"

        # Get data
        user = os.getenv('LOGS_USER')
        pw = os.getenv('LOGS_PW')
        req = requests.get(url, auth=HTTPBasicAuth(user, pw))
        items = jsonload(req.content)
        output = map(self.create_data_map, items.items())

        return {'posts': [*output]}, 200

    def post(self):
        lf = getLogger('file')
        try:
            # Vales from HANS come in form format, while values from Google
            # Forms come in json
            # TODO: Convert Google Forms to send form values rather than json
            url = f"{os.getenv('LOGS_BASE')}api/addpost.form"
            enc = be(f"{os.getenv('LOGS_USER')}:{os.getenv('LOGS_PW')}")
            headers = {'Authorization': f'Basic {enc}'}
            arg = request.form
            files = ''
            send_files = {}
            if arg:
                lf.debug("LOGS::form values from HANS")
                h = HTMLParser()

                body = h.unescape(arg['body'])
                lf.debug("LOGS::body: %s" % body)
                files = request.files.getlist("file")
                lf.debug("LOGS::files %s" % files)

                values = {'email': arg['email'] if 'email' in arg else '',
                          'username': arg['username'] if 'username' in arg
                          else '',
                          'appname': arg['appname'],
                          'subject': arg['subject'],
                          'body': body.encode('utf-8'),
                          'post_type': arg['post_type']}

                for idx, f in enumerate(files):
                    field = "file_%d" % idx
                    f.save("/tmp/%s" % f.filename)
                    send_files[field] = open("/tmp/%s" % f.filename, 'rb')
            else:
                arg = jsonload(request.data)

                # Set up date/time correctly
                odate = datetime.strptime(arg['obsdate'], SFMT)
                utcdt = odate.replace(tzinfo=pytz.UTC)
                hidt = utcdt.astimezone(pytz.timezone('Pacific/Honolulu'))

                # TODO: Allow editing?

                # Required fields
                values = {'email': arg['email'] if 'email' in arg else '',
                          'username': arg['user'] if 'user' in arg else '',
                          'appname': 'hvoapi',
                          'subject': arg['subject'],
                          'body': arg['text'],
                          'post_type': 'Seismic Daily Update'}

                # Optional Stuff
                values['obsdate'] = hidt.strftime(SFMT)
                values['keywords[]'] = 'Earthquake'

            lf.debug("LOGS::%s" % values)

#            if 'appname' in arg:
#                if arg['appname'] == 'test':
#                    return { 'status': 'ok' }, 201

            response = requests.post(url, data=values,
                                     headers=headers, files=send_files)
            lf.debug("LOGS::%s" % response.json)
            return {'status': 'ok'}, 201
        except Exception:
            lf.debug("LOGS::%s" % traceback.format_exc())
            return {'status': 'error'}, 400

    @staticmethod
    def create_data_map(data):
        item = {}
        item['id'] = data[1]['post_id']
        item['date'] = data[1]['date']
        item['user'] = data[1]['user']
        item['subject'] = data[1]['subject']
        item['type'] = data[1]['type']
        if data[1]['body']:
            item['body'] = (data[1]['body'].replace("\r\n", "<br>")
                                           .replace("\n", "<br>"))
        else:
            item['body'] = None
        if 'documents' in data[1]:
            item['documents'] = []
            for doc in data[1]['documents']:
                d = {}
                d['name'] = doc['name']
                d['url'] = doc['link']
                item['documents'].append(d)

        return item
