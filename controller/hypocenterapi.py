from common_constants import MAX_LINES
from flask import request, current_app
from flask_restful import Resource, reqparse
from model.hypocenter import Hypocenter
from sqlalchemy import func
from sqlalchemy.sql import text
from sys import float_info
from valverest.database import db4 as db
from valverest.util import create_date_from_input, date_to_j2k, j2k_to_date

# Values are N, S, E, W
_hawaii_coords = {
    'hawaii': [20.28, 18.88, -154.78, -156.10],
    'north_half': [20.28, 19.60, -154.78, -156.10],
    'south_half': [19.60, 18.88, -154.78, -156.10],
    'kilauea_summit': [19.44, 19.38, -155.23, -155.31],
    'kilauea_s_flank': [19.47, 19.15, -154.90, -155.50],
    'kilauea_erz': [19.55, 19.35, -154.80, -155.20],
    'kilauea_uerz': [19.41, 19.34, -155.18, -155.27],
    'kilauea_merz': [19.42, 19.34, -155.0, -155.215],
    'kilauea_lerz': [19.51, 19.35, -154.80, -154.95],
    'kilauea_swerz': [19.43, 19.15, -155.25, -155.46],
    'mauna_loa_summit': [19.62, 19.40, -155.53, -155.73],
    'mauna_loa_se_flank': [19.60, 19.25, -155.25, -155.75],
    'mauna_loa_swrz': [19.45, 19.15, -155.60, -155.80],
    'kaoiki': [19.55, 19.30, -155.30, -155.55],
    'loihi': [19.10, 18.60, -155.10, -155.40],
    'hawaiian_islands': [22.50, 18.50, -154.00, -161.00]
}

class HypocenterAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('north', type = float, required = False)
        self.reqparse.add_argument('south', type = float, required = False)
        self.reqparse.add_argument('east', type = float, required = False)
        self.reqparse.add_argument('west', type = float, required = False)
        self.reqparse.add_argument('geo', type = str, required = False,
                                   choices = _hawaii_coords.keys(), default = 'hawaii')
        self.reqparse.add_argument('rank', type = int, required = False, default = 0)
        self.reqparse.add_argument('starttime', type = str, required = True)
        self.reqparse.add_argument('endtime', type = str, required = False, default = 'now')
        self.reqparse.add_argument('timezone', type = str, required = False, default = 'hst')
        self.reqparse.add_argument('magmin', type = float, required = False, default = -2)
        self.reqparse.add_argument('magmax', type = float, required = False, default = 10)
        self.reqparse.add_argument('depthmin', type = float, required = False, default = -4)
        self.reqparse.add_argument('depthmax', type = float, required = False, default = str(float_info.max))
        self.reqparse.add_argument('nphasesmin', type = int, required = False, default = 0)
        self.reqparse.add_argument('nphasesmax', type = int, required = False, default = 100)
        self.reqparse.add_argument('remarks', type = str, required = False)
        self.reqparse.add_argument('herrmin', type = float, required = False, default = 0)
        self.reqparse.add_argument('herrmax', type = float, required = False, default = 50)
        self.reqparse.add_argument('verrmin', type = float, required = False, default = 0)
        self.reqparse.add_argument('verrmax', type = float, required = False, default = 50)
        self.reqparse.add_argument('rmsmin', type = float, required = False, default = 0)
        self.reqparse.add_argument('rmsmax', type = float, required = False, default = 5)
        super(HypocenterAPI, self).__init__()

    def get(self):
        if not request.args:
            return self.create_param_string(), 200

        if not current_app.debug:
            current_app.config['RESTFUL_JSON'] = {}

        args         = self.reqparse.parse_args()
        tz           = (args['timezone'] == 'hst')
        start, end   = create_date_from_input(args['starttime'], args['endtime'], tz)
        queryclauses = []
        orderby      = []

        if not args['north']:
            args['north'] = _hawaii_coords[args['geo']][0]
            args['south'] = _hawaii_coords[args['geo']][1]
            args['east'] = _hawaii_coords[args['geo']][2]
            args['west'] = _hawaii_coords[args['geo']][3]

        queryclauses.append(Hypocenter.lat.between(args['south'], args['north']))
        queryclauses.append(Hypocenter.timestamp.between(date_to_j2k(start, tz), date_to_j2k(end, tz)))

        # Handle crossing dateline
        if args['west'] <= args['east']:
            queryclauses.append(Hypocenter.lon.between(args['west'], args['east']))
        else:
            queryclauses.append(Hypocenter.lon >= args['west'] | Hypocenter.lon <= args['east'])

        queryclauses.append(Hypocenter.depth.between(args['depthmin'], args['depthmax']))
        queryclauses.append(Hypocenter.prefmag.between(args['magmin'], args['magmax']))
        queryclauses.append(Hypocenter.nphases.between(args['nphasesmin'], args['nphasesmax']))
        queryclauses.append(Hypocenter.rms.between(args['rmsmin'], args['rmsmax']))
        queryclauses.append(Hypocenter.herr.between(args['herrmin'], args['herrmax']))
        queryclauses.append(Hypocenter.verr.between(args['verrmin'], args['verrmax']))

        # Remarks
        if args['remarks']:
            queryclauses.append(Hypocenter.rmk == args['remarks'])

        orderby.append(Hypocenter.eid.asc())

        # Ranks - both order and filter
        if args['rank'] != 0:
            queryclauses.append(Hypocenter.rid == args['rank'])
        else:
            orderby.append(Hypocenter.rid.desc())

        q = Hypocenter.query.filter(*queryclauses).order_by(*orderby)
        try:
            q = q.limit(MAX_LINES['HYPOCENTER'])
        except KeyError:
            pass
        data = q.all()

        output = []
        Date   = j2k_to_date
        List   = output.append
        for d in data:
            List({ 'date': Date(d.timestamp, tz).strftime('%Y-%m-%d %H:%M:%S.%f'), 'rank': d.rank.name,
                   'depth': d.depth, 'lat': d.lat, 'lon': d.lon, 'prefMag': d.prefmag })
        return { 'nr': len(data),
                 'location': ', '.join([str(args['north']), str(args['south']), str(args['east']), str(args['west'])]),
                 'records': output }, 200

    @staticmethod
    def create_param_string():
        if not current_app.debug:
            settings = current_app.config.get('RESTFUL_JSON', {})
            settings.setdefault('indent', 4)
            settings.setdefault('sort_keys', True)
            current_app.config['RESTFUL_JSON'] = settings

        params = {}
        params['starttime'] = {'type': 'string', 'required': 'yes',
                              'note': 'Will also accept things like -6m for last six months.',
                              'format': 'yyyy[MMdd[hhmm]]'}
        params['endtime'] = {'type': 'string', 'required': 'no', 'format': 'yyyy[MMdd[hhmm]]', 'default': 'now'}
        params['rank'] = {'type': 'int', 'required': 'no', 'default': 0,
                         'note': 'A rank of 0 will return the best possible rank.'}
        params['timezone'] = {'type': 'string', 'required': 'no', 'default': 'hst'}
        params['north'] = {'type': 'float', 'required': 'no', 'note':
                          'Either a set of N,S,E,W coordinates or a geo value must exist.'}
        params['south'] = {'type': 'float', 'required': 'no', 'note':
                          'Either a set of N,S,E,W coordinates or a geo value must exist.'}
        params['east'] = {'type': 'float', 'required': 'no', 'note':
                          'Either a set of N,S,E,W coordinates or a geo value must exist.'}
        params['west'] = {'type': 'float', 'required': 'no', 'note':
                          'Either a set of N,S,E,W coordinates or a geo value must exist.'}
        params['geo'] = {'type': 'string', 'required': 'no', 'default': 'hawaii',
                        'note': 'Either a set of N,S,E,W coordinates or a geo value must exist.',
                        'options': _hawaii_coords.keys() }
        params['magmin'] = {'type': 'float', 'required': 'no', 'default': -2}
        params['magmax'] = {'type': 'float', 'required': 'no', 'default': 10}
        params['depthmin'] = {'type': 'float', 'required': 'no', 'default': 0}
        params['depthmax'] = {'type': 'float', 'required': 'no', 'default': float_info.max}
        params['nphasesmin'] = {'type': 'int', 'required': 'no', 'default': 0}
        params['nphasesmax'] = {'type': 'int', 'required': 'no', 'default': 100}
        params['herrmin'] = {'type': 'float', 'required': 'no', 'default': 0}
        params['herrmax'] = {'type': 'float', 'required': 'no', 'default': 50}
        params['verrmin'] = {'type': 'float', 'required': 'no', 'default': 0}
        params['verrmax'] = {'type': 'float', 'required': 'no', 'default': 50}
        params['rmsmin'] = {'type': 'float', 'required': 'no', 'default': 0}
        params['rmsmax'] = {'type': 'float', 'required': 'no', 'default': 5}
        params['remarks'] = {'type': 'string', 'required': 'no'}
        return params
