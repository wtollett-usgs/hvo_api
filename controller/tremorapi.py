from flask import request, current_app
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import settings as json_settings
from model.tremor import catalog, station
from sqlalchemy import func, distinct
from sqlalchemy.sql.expression import cast
from valverest.database import db
from valverest.util import create_date_from_input

import random

class TremorAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('methodid', type = int, required = True)
        self.reqparse.add_argument('starttime', type = str, required = True)
        self.reqparse.add_argument('endtime', type = str, required = True)
        self.reqparse.add_argument('retvals', type = str, required = False, default = 'all')
        self.reqparse.add_argument('region', type = str, required = False, default = 'all')
        super(TremorAPI, self).__init__()

    def get(self):
        # Return expected parameter output, also set indent settings
        if not request.args:
            return self.create_param_string(), 200

        if (not current_app.debug) and (json_settings and json_settings['indent']):
            json_settings['indent'] = None

        args      = self.reqparse.parse_args()
        starttime = args['starttime']
        endtime   = args['endtime']
        methodid  = args['methodid']
        region    = args['region'].upper()
        retvals   = args['retvals'].lower()
        sd,ed     = create_date_from_input(starttime, endtime)
        data      = []
        output    = []
        List      = output.append

        # Set up where clauses there are used by all methods
        q_items = []
        w_items = []
        w_items.append(catalog.starttime.between(sd,ed))
        w_items.append(catalog.methodid == methodid)
        w_items.append(catalog.iseq == 0)

        # Check if this is multiple regions at once
        # Note: This is currently only useful with station query
        if ',' in region:
            w_items.append(catalog.region.in_(region.split(',')))
        elif region == 'ALL':
            w_items.append(catalog.region != 'LO')
        else:
            w_items.append(catalog.region == region)
        w_items.append(catalog.iseq == 0)

        if retvals == 'dates':
            q_items.append(cast(catalog.starttime, db.Date).label('date'))
            q_items.append(func.count(distinct(catalog.evid)).label('total'))

            data = db.session.query(*q_items).filter(*w_items).group_by(cast(catalog.starttime, db.Date)).all()
            for d in data:
                List({ 'date': d.date.strftime("%Y-%m-%d"),
                       'count': d.total})
        else:
            data = catalog.query.filter(*w_items).order_by(catalog.starttime.desc()).all()
            if retvals == 'stations':
                if len(data) > 5000:
                    rindices = random.sample(range(0, len(data)), 5000)
                    rindices.sort()
                    for i in range(0, len(rindices)):
                        d = data[rindices[i]]
                        List({ 'starttime': d.starttime.strftime("%Y-%m-%d %H:%M:%S.%f"),
                               'latitude': float(d.latitude),
                               'longitude': float(d.longitude),
                               'depth': float(d.depth),
                               'evid': d.evid,
                               'region': d.region,
                               'stations': ['%s.%s' % (x.sta, x.chan) for x in d.stations] })
                    return { 'nr': len(data),
                             'records': output,
                             'shown': len(rindices) }, 200
                else:
                    for d in data:
                        List({ 'starttime': d.starttime.strftime("%Y-%m-%d %H:%M:%S.%f"),
                               'latitude': float(d.latitude),
                               'longitude': float(d.longitude),
                               'depth': float(d.depth),
                               'evid': d.evid,
                               'region': d.region,
                               'stations': ['%s.%s' % (x.sta, x.chan) for x in d.stations] })
            else:
                for d in data:
                    List({ 'starttime': d.starttime.strftime("%Y-%m-%d %H:%M:%S.%f"),
                           'latitude': float(d.latitude),
                           'longitude': float(d.longitude),
                           'depth': float(d.depth),
                           'evid': d.evid })
        return { 'nr': len(data),
                 'records': output }, 200

    @staticmethod
    def create_param_string():
        if not current_app.debug:
            json_settings['indent']    = 4
            json_settings['sort_keys'] = True

        params = {}
        params['starttime'] = { 'type': 'string', 'required': 'yes',
                                'note': '',
                                'format': 'yyyy[MMdd[hhmm]]' }
        params['endtime']  = { 'type': 'string', 'required': 'yes', 'format': 'yyyy[MMdd[hhmm]]'}
        params['methodid'] = { 'type': 'integer', 'required': 'yes', 'note': ''}
        params['region']   = { 'type': 'string', 'required': 'no', 'default': 'all'}
        params['retvals']  = { 'type': 'string', 'required': 'no', 'default': 'all',
                               'options': ['all', 'dates', 'stations']}
        return params
