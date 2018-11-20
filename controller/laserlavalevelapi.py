# -*- coding: utf-8 -*-
from .common_constants import FFMT
from flask import request, current_app
from flask_restful import Resource, reqparse
from model.laserlavalevel import LaserLavaLevel
from valverest.util import create_date_from_input, date_to_j2k, j2k_to_date


class LaserLavaLevelAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('channel', type=str, required=False,
                                   default='HMM')
        self.reqparse.add_argument('rank', type=str, required=False, default=1)
        self.reqparse.add_argument('starttime', type=str, required=True)
        self.reqparse.add_argument('endtime', type=str, required=False,
                                   default='now')
        self.reqparse.add_argument('timezone', type=str, required=False,
                                   default='hst')
        super(LaserLavaLevelAPI, self).__init__()

    def get(self):
        if not request.args:
            return self.create_param_string(), 200

        if not current_app.debug:
            current_app.config['RESTFUL_JSON'] = {}

        args = self.reqparse.parse_args()
        tz = (args['timezone'].lower() == 'hst')
        start, end = create_date_from_input(args['starttime'],
                                            args['endtime'], tz)
        w_items = [LaserLavaLevel.timestamp.between(date_to_j2k(start, tz),
                                                    date_to_j2k(end, tz))]
        data = LaserLavaLevel.query.filter(*w_items).all()

        output = []
        append = output.append
        jtod = j2k_to_date
        for d in data:
            if d.sealevel is None:
                append({'date': jtod(d.timestamp, tz).strftime(FFMT),
                        'rank': d.rank.name,
                        'sealevel': d.sealevel,
                        'overlook': d.overlook})
            else:
                append({'date': jtod(d.timestamp, tz).strftime(FFMT),
                        'rank': d.rank.name,
                        'sealevel': (d.sealevel * d.translation.csealevel
                                     + d.translation.dsealevel),
                        'overlook': (d.overlook * d.translation.coverlook
                                     + d.translation.doverlook)})
        return {'nr': len(data),
                'records': output}, 200

    @staticmethod
    def create_param_string():
        if not current_app.debug:
            settings = current_app.config.get('RESTFUL_JSON', {})
            settings.setdefault('indent', 4)
            settings.setdefault('sort_keys', True)
            current_app.config['RESTFUL_JSON'] = settings

        params = {}
        params['channel'] = {'type': 'string', 'required': 'no',
                             'note': 'Can be comma-separated list.',
                             'default': 'HMM'}
        params['starttime'] = {'type': 'string', 'required': 'yes',
                               'note': ('Will also accept things like -6m '
                                        'for last six months.'),
                               'format': 'yyyy[MMdd[hhmm]]'}
        params['endtime'] = {'type': 'string', 'required': 'no',
                             'format': 'yyyy[MMdd[hhmm]]', 'default': 'now'}
        params['rank'] = {'type': 'int', 'required': 'no', 'default': 1,
                          'note': ('A rank of 0 will return the '
                                   'best possible rank.')}
        params['timezone'] = {'type': 'string', 'required': 'no',
                              'default': 'hst'}
        return params
