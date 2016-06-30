from common_constants import MAX_LINES, DS_OPTIONS
from flask import request, current_app
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import settings as json_settings
from valverest.database import db6 as db
from valverest.util import create_date_from_input, date_to_j2k, j2k_to_date

import model.strain as strain

_series_options = ['dt01', 'dt02', 'barometer']

class StrainAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('channel', type = str, required = True)
        self.reqparse.add_argument('rank', type = int, required = False, default = 2)
        self.reqparse.add_argument('series', type = str, required = False, default = 'dt01')
        self.reqparse.add_argument('starttime', type = str, required = True)
        self.reqparse.add_argument('endtime', type = str, required = False, default = 'now')
        self.reqparse.add_argument('timezone', type = str, required = False, default = 'hst')
        self.reqparse.add_argument('debias', type = str, required = False, default = 'mean')
        super(StrainAPI, self).__init__()

    def get(self):
        if not request.args:
            return self.create_param_string(), 200

        if (not current_app) and (json_settings and json_settings['indent']):
            json_settings['indent'] = None

        args = self.reqparse.parse_args()

        channels = args['channel'].split(',')
        unknown  = set([x.upper() for x in channels]).difference(strain._tablenames)
        if len(unknown) > 0:
            return { 'Error': 'unknown channel(s): %s' % ','.join(unknown) }

        series  = args['series'].split(',')
        unknown = set([x.lower() for x in series]).difference(_series_options)
        if len(unknown) > 0:
            return { 'Error': 'unknown series: %s' % ','.join(unknown) }

        tz         = (args['timezone'].lower() == 'hst')
        start, end = create_date_from_input(args['starttime'], args['endtime'], tz)
        output     = {}
        count      = 0

        for channel in channels:
            queryclauses = []
            orderby      = []
            cname        = getattr(strain, channel.upper())

            # Set up query filters
            queryclauses.append(cname.timestamp.between(date_to_j2k(start, tz), date_to_j2k(end, tz)))

            # Set up order by values
            orderby.append(cname.timestamp.asc())

            if args['rank'] == 0:
                orderby.append(cname.rid.desc())
            else:
                queryclauses.append(cname.rid == args['rank'])

            q = cname.query.filter(*queryclauses).order_by(*orderby)
            try:
                q = q.limit(MAX_LINES['STRAIN'])
            except KeyError:
                pass
            data = q.all()

            output[channel] = []
            Date            = j2k_to_date
            List            = output[channel].append

            # Means
            if args['debias'] == 'mean':
                m01        = sum([x.dt01 for x in data]) / float(len(data)) if 'dt01' in series else 0
                m02        = sum([x.dt02 for x in data]) / float(len(data)) if 'dt02' in series else 0
                mbarometer = sum([x.barometer for x in data]) / float(len(data)) if 'barometer' in series else 0
            else:
                m01        = 0
                m02        = 0
                mbarometer = 0

            for d in data:
                a = { 'date': Date(d.timestamp, tz).strftime('%Y-%m-%d %H:%M:%S.%f'),
                      'rank': d.rank.name }

                if 'dt01' in series:
                    a['dt01'] = (d.dt01 - m01) * d.translation.cdt01 + d.translation.ddt01
                if 'dt02' in series:
                    a['dt02'] = (d.dt02 - m02) * d.translation.cdt02 + d.translation.ddt02
                if 'barometer' in series:
                    a['barometer'] = (d.barometer - mbarometer) * d.translation.barometer + d.translation.barometer
                List(a)
            count += len(data)
        return { 'nr': count,
                 'records': output }, 200

    @staticmethod
    def create_param_string():
        if not current_app.debug:
            json_settings['indent'] = 4
            json_settings['sort_keys'] = True

        params = {}
        params['channel'] = {'type': 'string', 'required': 'yes', 'note': 'Can be comma-separated list.',
                            'options': strain._tablenames}
        params['starttime'] = {'type': 'string', 'required': 'yes',
                              'note': 'Will also accept things like -6m for last six months.',
                              'format': 'yyyy[MMdd[hhmm]]'}
        params['endtime'] = {'type': 'string', 'required': 'no', 'format': 'yyyy[MMdd[hhmm]]', 'default': 'now'}
        params['rank'] = {'type': 'int', 'required': 'no', 'default': 2,
                         'note': 'A rank of 0 will return the best possible rank.'}
        params['timezone'] = {'type': 'string', 'required': 'no', 'default': 'hst'}
        params['series'] = {'type': 'string', 'required': 'no', 'note': 'Can be comma-separated list.',
                            'default': 'dt01', 'options': _series_options}
        params['debias'] = {'type': 'string', 'required': 'no', 'default': 'mean', 'options': 'mean, none'}
        return params
