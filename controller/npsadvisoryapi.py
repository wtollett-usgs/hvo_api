from .common_constants import DFMT, MAX_LINES
from flask import request, current_app
from flask_restful import Resource, reqparse
from valverest.util import create_date_from_input, date_to_j2k, j2k_to_date

import model.npsadvisory as npsadvisory

_series_options = ['avgso2', 'pm25', 'windspeed', 'winddir', 'winddirsd',
                   'temperature', 'humidity', 'pressure', 'rainfall',
                   'inttemp', 'instvolt', 'cal']


class NPSAdvisoryAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('channel', type=str, required=True)
        self.reqparse.add_argument('rank', type=int, required=False, default=1)
        self.reqparse.add_argument('series', type=str, required=False,
                                   default='avgso2')
        self.reqparse.add_argument('starttime', type=str, required=True)
        self.reqparse.add_argument('endtime', type=str, required=False,
                                   default='now')
        self.reqparse.add_argument('timezone', type=str, required=False,
                                   default='hst')
        super(NPSAdvisoryAPI, self).__init__()

    def get(self):
        if not request.args:
            return self.create_param_string(), 200

        if not current_app.debug:
            current_app.config['RESTFUL_JSON'] = {}

        args = self.reqparse.parse_args()

        channels = args['channel'].split(',')
        unknown = set([x.upper() for x in channels]) \
            .difference(npsadvisory._tablenames)
        if len(unknown) > 0:
            return {'Error': f"unknown channel(s): {','.join(unknown)}"}

        series = args['series'].split(',')
        unknown = set([x.lower() for x in series]).difference(_series_options)
        if len(unknown) > 0:
            return {'Error': f"unknown series: {','.join(unknown)}"}

        tz = (args['timezone'].lower() == 'hst')
        start, end = create_date_from_input(args['starttime'], args['endtime'],
                                            tz)
        output = {}
        count = 0

        for channel in channels:
            queryclauses = []
            orderby = []
            cname = getattr(npsadvisory, channel.upper())

            # Set up query filters
            queryclauses.append(cname.timestamp.between(date_to_j2k(start, tz),
                                date_to_j2k(end, tz)))

            # Set up order by values
            orderby.append(cname.timestamp.asc())

            if args['rank'] == 0:
                orderby.append(cname.rid.desc())
            else:
                queryclauses.append(cname.rid == args['rank'])

            q = cname.query.filter(*queryclauses).order_by(*orderby)
            try:
                q = q.limit(MAX_LINES['NPSADVISORY'])
            except KeyError:
                pass
            data = q.all()

            output[channel] = []
            Date = j2k_to_date
            List = output[channel].append

            for d in data:
                a = {'date': Date(d.timestamp, tz).strftime(DFMT),
                     'rank': d.rank.name}

                for i in args['series'].split(','):
                    val = getattr(d, i.lower())
                    if val:
                        val = val * getattr(d.translation, f'c{i.lower()}') +\
                              getattr(d.translation, f'd{i.lower()}')
                    a[i] = val
                List(a)
            count += len(data)
        return {'nr': count,
                'records': output}, 200

    @staticmethod
    def create_param_string():
        if not current_app.debug:
            settings = current_app.config.get('RESTFUL_JSON', {})
            settings.setdefault('indent', 4)
            settings.setdefault('sort_keys', True)
            current_app.config['RESTFUL_JSON'] = settings

        params = {}
        params['channel'] = {'type': 'string', 'required': 'yes',
                             'note': 'Can be comma-separated list.',
                             'options': npsadvisory._tablenames}
        params['starttime'] = {'type': 'string', 'required': 'yes',
                               'note': ('Will also accept things like -6m '
                                        'for last six months.'),
                               'format': 'yyyy[MMdd[hhmm]]'}
        params['endtime'] = {'type': 'string', 'required': 'no',
                             'format': 'yyyy[MMdd[hhmm]]', 'default': 'now'}
        params['rank'] = {'type': 'int', 'required': 'no', 'default': 1,
                          'note': ('A rank of 0 will return the best '
                                   'possible rank.')}
        params['timezone'] = {'type': 'string', 'required': 'no',
                              'default': 'hst'}
        params['series'] = {'type': 'string', 'required': 'no',
                            'note': 'Can be comma-separated list.',
                            'default': 'dt01', 'options': _series_options}
        return params
