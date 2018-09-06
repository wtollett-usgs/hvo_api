from .common_constants import MAX_LINES, DS_OPTIONS
from flask import request, current_app
from flask_restful import Resource, reqparse
from valverest.database import db6 as db
from valverest.util import create_date_from_input, date_to_j2k, j2k_to_date

import model.triggers as triggers

class TriggersAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('channel', type = str, required = True)
        self.reqparse.add_argument('starttime', type = str, required = True)
        self.reqparse.add_argument('endtime', type = str, required = False, default = 'now')
        self.reqparse.add_argument('timezone', type = str, required = False, default = 'hst')

        super(TriggersAPI, self).__init__()

    def get(self):
        if not request.args:
            return self.create_param_string(), 200

        if not current_app.debug:
            current_app.config['RESTFUL_JSON'] = {}

        args = self.reqparse.parse_args()

        channels = args['channel'].split(',')
        unknown  = set([x.upper() for x in channels]).difference(triggers._tablenames)
        if len(unknown) > 0:
            return { 'Error': 'unknown channel(s): %s' % ','.join(unknown) }

        tz         = (args['timezone'].lower() == 'hst')
        start, end = create_date_from_input(args['starttime'], args['endtime'], tz)
        output     = {}
        count      = 0

        for channel in channels:
            queryclauses = []
            orderby      = []
            cname        = getattr(triggers, channel.upper())

            # Set up query filters
            queryclauses.append(cname.timestamp.between(date_to_j2k(start, tz), date_to_j2k(end, tz)))

            # Set up order by values
            orderby.append(cname.timestamp.asc())

            q = cname.query.filter(*queryclauses).order_by(*orderby)
            try:
                q = q.limit(MAX_LINES['TRIGGERS'])
            except KeyError:
                pass
            data = q.all()

            output[channel] = []
            Date            = j2k_to_date
            List            = output[channel].append

            for d in data:
                a = { 'date': Date(d.timestamp, tz).strftime('%Y-%m-%d %H:%M:%S'),
                      'triggers': d.triggers }
                
                List(a)
            count += len(data)
        return { 'nr': count,
                 'records': output }, 200

    @staticmethod
    def create_param_string():
        if not current_app.debug:
            settings = current_app.config.get('RESTFUL_JSON', {})
            settings.setdefault('indent', 4)
            settings.setdefault('sort_keys', True)
            current_app.config['RESTFUL_JSON'] = settings

        params = {}
        params['channel'] = {'type': 'string', 'required': 'yes', 'note': 'Can be comma-separated list.',
                            'options': triggers._tablenames}
        params['starttime'] = {'type': 'string', 'required': 'yes',
                              'note': 'Will also accept things like -6m for last six months.',
                              'format': 'yyyy[MMdd[hhmm]]'}
        params['endtime'] = {'type': 'string', 'required': 'no', 'format': 'yyyy[MMdd[hhmm]]', 'default': 'now'}
        params['timezone'] = {'type': 'string', 'required': 'no', 'default': 'hst'}
        
        return params
