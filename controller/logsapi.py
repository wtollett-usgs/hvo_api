from datetime import datetime
from flask import request, current_app
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import settings as json_settings
from json import loads as jsonload
from logging import getLogger
from model import hvologs
from valverest.database import db2 as hvodb

import HTMLParser
import pytz
import urllib
import urllib2
import traceback

class LogsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('op', type = str, required = False, default = 'time')
        self.reqparse.add_argument('num', type = int, required = False, default = 20)
        super(LogsAPI, self).__init__()

    def get(self):
        # Return expected parameter output, also set indent settings
        if not request.args:
            return self.create_param_string(), 200

        if (not current_app.debug) and (json_settings and json_settings['indent']):
            json_settings['indent'] = None

        output = []
        args   = self.reqparse.parse_args()
        cname  = hvologs
        db     = hvodb

        if 'op' in args and args['op'] == 'time':
            post = cname.Post.query.order_by(cname.Post.observtime.desc()).first()
            return { 'id': post.obsID, 'observtime': post.observtime.strftime("%Y-%m-%d %H:%M:%S"),
                     'obsdate': post.obsdate.strftime("%Y-%m-%d %H:%M:%S") }, 200
        else:
            posts  = cname.Post.query.filter(cname.Post.parentID==None).order_by(cname.Post.sortdate.desc()).limit(args['num']).all()
            output = map(self.create_data_map, posts)
            return { 'nr': len(posts), 'posts': output }, 200

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

                values = {'email': arg['email'],
                          'username': arg['username'],
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
                          'post_type': 'Seismology'}

                #Optional Stuff
                values['obsdate'] = hidt.strftime('%Y-%m-%d %H:%M:%S')
                values['keywords[]'] = 'Earthquake'

            lf.debug(values)
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
        item = {}
        item['title'] = data.subject
        item['text'] = data.obstext
        item['user'] = '%s %s' % (data.user.first, data.user.last)
        item['postdate'] = data.observtime.strftime('%Y-%m-%d %H:%M:%S.%f')
        item['sortdate'] = data.sortdate.strftime('%Y-%m-%d %H:%M:%S.%f')

        return item

    @staticmethod
    def create_param_string():
        if not current_app.debug:
            json_settings['indent']    = 4
            json_settings['sort_keys'] = True

        params = {}
        params['op'] = { 'type': 'string', 'required': 'no', 'options': 'time, posts',
                         'note': 'Returns datetime for last record in the database. Other parameters not required.'}
        params['num'] = { 'type': 'int', 'required': 'no', 'default': 20, 'note': 'Number of log entries to return'}
        return params
