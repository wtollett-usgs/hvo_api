from common_constants import MAX_LINES, DS_OPTIONS
from flask import request, current_app
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import settings as json_settings
from valverest.database import db3 as db
from valverest.util import create_date_from_input, date_to_j2k, j2k_to_date

import model.flyspec as flyspec

_series_options = ['bstflux', 'bstfluxmean', 'bstfluxmeanstdev', 'flux01', 'fluxsdh', 'ps', 'pd', 'specs', 'nflag',
                   'sflag', 'colpath', 'satpix', 'inttime', 'boxtemp', 'sysvolt', 'current']

class FlyspecAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('channel', type = str, required = True)
        self.reqparse.add_argument('rank', type = int, required = False, default = 2)
        self.reqparse.add_argument('series', type = str, required = False, default = 'bstflux')
        self.reqparse.add_argument('starttime', type = str, required = True)
        self.reqparse.add_argument('endtime', type = str, required = False, default = 'now')
        self.reqparse.add_argument('timezone', type = str, required = False, default = 'hst')
        super(FlyspecAPI, self).__init__()

    def get(self):
        if not request.args:
            return self.create_param_string(), 200

        if (not current_app) and (json_settings and json_settings['indent']):
            json_settings['indent'] = None

        args = self.reqparse.parse_args()

        channels = args['channel'].split(',')
        unknown  = set([x.upper() for x in channels]).difference(flyspec._tablenames)
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
            cname        = getattr(flyspec, channel.upper())

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
                q = q.limit(MAX_LINES['FLYSPEC'])
            except KeyError:
                pass
            data = q.all()

            output[channel] = []
            Date            = j2k_to_date
            List            = output[channel].append
            for d in data:
                a = { 'date': Date(d.timestamp, tz).strftime('%Y-%m-%d %H:%M:%S.%f'),
                      'rank': d.rank.name }

                for i in args['series'].split(','):
                    a[i] = getattr(d, i.lower())
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
                            'options': flyspec._tablenames}
        params['starttime'] = {'type': 'string', 'required': 'yes',
                              'note': 'Will also accept things like -6m for last six months.',
                              'format': 'yyyy[MMdd[hhmm]]'}
        params['endtime'] = {'type': 'string', 'required': 'no', 'format': 'yyyy[MMdd[hhmm]]', 'default': 'now'}
        params['rank'] = {'type': 'int', 'required': 'no', 'default': 2,
                         'note': 'A rank of 0 will return the best possible rank.'}
        params['timezone'] = {'type': 'string', 'required': 'no', 'default': 'hst'}
        params['series'] = {'type': 'string', 'required': 'no', 'note': 'Can be comma-separated list.',
                            'default': 'bstflux', 'options': _series_options}
        return params
