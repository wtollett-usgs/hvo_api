from datetime import datetime
from flask import request, current_app
from flask.ext.restful import Resource
from flask.ext.restful.representations.json import settings as json_settings
from json import loads as jsonload
from logging import getLogger

import HTMLParser
import pytz
import urllib
import urllib2
import traceback

class LogsAPI(Resource):
    def __init__(self):
        super(LogsAPI, self).__init__()

    def get(self):
        if (not current_app.debug) and (json_settings and json_settings['indent']):
            json_settings['indent'] = None

        url = "https://hvointernal.wr.usgs.gov/hvo_logs/api/getposts"
        headers = {'Authorization': ***REMOVED***}

        # Get data
        req      = urllib2.Request(url, '', headers)
        response = urllib2.urlopen(req)
        items    = jsonload(response.read())
        output   = map(self.create_data_map, items.iteritems())

        return { 'posts': output }, 200

    def post(self):
        lf = getLogger('file')
        try:
            # Vales from HANS come in form format, while values from Google Forms come in json
            # TODO: Convert Google Forms to send form values rather than json
            url = "https://hvointernal.wr.usgs.gov/hvo_logs/api/addpost.form"
            headers = {'Authorization': ***REMOVED***}
            arg = request.form
            if arg:
                lf.debug('form values from HANS')
                h = HTMLParser.HTMLParser()

                #s = 'Attempting to insert log entry for postdate=%s, obsdate=%s, user=%s, subject=%s'
                #lf.debug(s % (arg['postdate'], arg['obsdate'], arg['user'], arg['subject']))
                body = h.unescape(arg['body'])
                lf.debug("body: %s" % body)

                values = {'email': arg['email'] if 'email' in arg else '',
                          'username': arg['username'] if 'username' in arg else '',
                          'appname': arg['appname'],
                          'subject': arg['subject'],
                          'body': body.encode('utf-8'),
                          'post_type': arg['post_type']}
            else:
                arg = jsonload(request.data)

                # Set up date/time correctly
                odate = datetime.strptime(arg['obsdate'], '%Y-%m-%d %H:%M:%S')
                utcdt = odate.replace(tzinfo=pytz.UTC)
                hidt  = utcdt.astimezone(pytz.timezone('Pacific/Honolulu'))

                # TODO: Allow editing?

                # Required fields
                values = {'email': arg['user'],
                          'appname': 'hvoapi',
                          'subject': arg['subject'],
                          'body': arg['text'],
                          'post_type': 'Seismic Daily Update'}

                #Optional Stuff
                values['obsdate'] = hidt.strftime('%Y-%m-%d %H:%M:%S')
                values['keywords[]'] = 'Earthquake'

            lf.debug(values)

            if 'appname' in arg:
                if arg['appname'] == 'test':
                    return { 'status': 'ok' }, 201

            data = urllib.urlencode(values)
            req = urllib2.Request(url, data, headers)
            response = urllib2.urlopen(req)
            lf.debug(response.read())
            return { 'status': 'ok' }, 201
        except Exception:
            lf.debug(traceback.format_exc())
            return { 'status': 'error' }, 400

    @staticmethod
    def create_data_map(data):
        item              = {}
        item['date']      = data[1]['date']
        item['user']      = data[1]['user']
        item['subject']   = data[1]['subject']
        item['type']      = data[1]['type']
        item['body']      = data[1]['body'].replace("\r\n", "<br>").replace("\n", "<br>")
        if 'documents' in data[1]:
            item['documents'] = []
            for doc in data[1]['documents']:
                d         = {}
                d['name'] = doc['name']
                d['url']  = doc['link']
                item['documents'].append(d)

        return item
