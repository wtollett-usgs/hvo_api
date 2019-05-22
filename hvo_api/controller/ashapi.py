# -*- coding: utf-8 -*-
from .common_constants import FFMT
from flask import request, current_app
from flask_restful import Resource, reqparse
from model.ash import HMM
from sqlalchemy import func, exc
from valverest.database import db
from valverest.util import (
    clean_input,
    j2k_to_date,
    create_date_from_input,
    date_to_j2k
)

import json
import logging


class AshAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('op', type=str, required=False)
        self.reqparse.add_argument('starttime', type=str, required=False)
        self.reqparse.add_argument('endtime', type=str, required=False,
                                   default='now')
        self.reqparse.add_argument('timezone', type=str, required=False,
                                   default='hst')
        super(AshAPI, self).__init__()

    def get(self):
        # Return expected parameter output, also set indent settings
        if not request.args:
            return self.create_param_string(), 200

        if not current_app.debug:
            current_app.config['RESTFUL_JSON'] = {}

        args = self.reqparse.parse_args()
        if 'op' in args and args['op'] == 'time':
            t = db.session.query(func.max(HMM.timestamp)).one()[0]
            d = j2k_to_date(t, (args['timezone'] == 'HST')).strftime(FFMT)
            return {'HMM': d}, 200
        else:
            starttime = args['starttime']
            endtime = args['endtime']
            tz = (args['timezone'].lower() == 'hst')
            sd, ed = create_date_from_input(starttime, endtime, tz)
            jsd = date_to_j2k(sd, tz)
            jed = date_to_j2k(ed, tz)
            data = (HMM
                    .query.filter(HMM.timestamp.between(jsd, jed))
                    .order_by(HMM.timestamp.desc()).all())
            output = []
            Date = j2k_to_date
            List = output.append
            for d in data:
                List({'date': Date(d.timestamp, tz).strftime(FFMT),
                      'accumrate': d.accumrate,
                      'percentjuvenile': d.percentjuvenile})
            return {'nr': len(data),
                    'records': output}, 200

    def post(self):
        lf = logging.getLogger('file')
        try:
            args = json.loads(request.data)
            for arg in args:
                arg = clean_input(arg)
                d = date_to_j2k(arg['date'], False)
                item = HMM.query.filter_by(timestamp=d).first()
                if item:
                    lf.debug('Updating item for j2ksec: ' + str(d))
                    if arg['ar'] != '':
                        item.accumrate = '%.3f' % float(arg['ar'])
                    else:
                        item.accumrate = None
                    if arg['pj'] != '':
                        item.percentjuvenile = '%.2f' % float(arg['pj'])
                    else:
                        item.percentjuvenile = None
                else:
                    item = HMM(time=arg['date'], ar=arg['ar'], pj=arg['pj'])
                    lf.debug("Attempting to insert ash observation for"
                             "date=%s, accumrate=%s, percentjuvenile=%s" %
                             (arg['date'], arg['ar'], arg['pj']))
                    db.session.add(item)
            db.session.commit()
            lf.debug("Item added/updated")
            return {'status': 'ok'}, 201
        except exc.SQLAlchemyError as e:
            lf.debug(f"Insert failed: {e}")
            return {'status': 'error inserting item, check logs'}, 200

    @staticmethod
    def create_param_string():
        if not current_app.debug:
            settings = current_app.config.get('RESTFUL_JSON', {})
            settings.setdefault('indent', 4)
            settings.setdefault('sort_keys', True)
            current_app.config['RESTFUL_JSON'] = settings

        params = {}
        params['starttime'] = {'type': 'string', 'required': 'yes',
                               'note': ('Will also accept things like -6m for '
                                        'last 6 months.'),
                               'format': 'yyyy[MMdd[hhmm]]'}
        params['endtime'] = {'type': 'string', 'required': 'no',
                             'format': 'yyyy[MMdd[hhmm]]', 'default': 'now'}
        params['timezone'] = {'type': 'string', 'required': 'no',
                              'default': 'hst'}
        params['op'] = {'type': 'string', 'required': 'no', 'options': 'time',
                        'note': ('Returns datetime for last record in the '
                                 'database. Other paramaters not required.')}
        return params
