from .common_constants import MAX_LINES, DS_OPTIONS
from flask import request, current_app
from flask_restful import Resource, reqparse
from sqlalchemy import func
from sqlalchemy.sql import text
from valverest.database import db5 as db
from valverest.util import create_date_from_input, date_to_j2k, j2k_to_date

import model.rsam as rsam

class RSAMAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('channel', type = str, required = False)
        self.reqparse.add_argument('starttime', type = str, required = True)
        self.reqparse.add_argument('endtime', type = str, required = False, default = 'now')
        self.reqparse.add_argument('timezone', type = str, required = False, default = 'hst')
        self.reqparse.add_argument('downsample', type = str, required = False, default = 'none')
        self.reqparse.add_argument('dsint', type = int, required = False)
        super(RSAMAPI, self).__init__()

    def get(self):
        if not request.args:
            return self.create_param_string(), 200

        if not current_app.debug:
            current_app.config['RESTFUL_JSON'] = {}

        args     = self.reqparse.parse_args()
        channels = args['channel'].split(',')
        if set([x.upper() for x in channels]).difference(rsam._tablenames):
            return { 'Error': 'unknown channel' }

        tz         = (args['timezone'] == 'hst')
        start, end = create_date_from_input(args['starttime'], args['endtime'], tz)
        output     = {}
        count      = 0
        for channel in channels:
            queryclauses = []
            orderby      = []
            cname        = getattr(rsam, channel.upper())

            queryclauses.append(cname.timestamp.between(date_to_j2k(start, tz), date_to_j2k(end, tz)))
            orderby.append(cname.timestamp.asc())

            if args['downsample'] == 'none':
                q = cname.query.filter(*queryclauses).order_by(*orderby)
                try:
                    q = q.limit(MAX_LINES['RSAM'])
                except KeyError:
                    pass
                data = q.all()
            elif args['downsample'] == 'decimate':
                interval = args['dsint']
                dbname   = 'v3_hvo_seismic_rsam$rsam'
                s        = "SELECT * FROM(SELECT fullquery.*, @row := @row+1 AS rownum FROM(SELECT j2ksec "\
                           "as timestamp, rsam FROM " + dbname + "." + cname.__tablename__ + " WHERE j2ksec "\
                           "BETWEEN :st AND :et ORDER BY j2ksec ASC) fullquery, (SELECT @row := 0) r) WHERE ranked "\
                           "rownum % :dsint = 1"
                try:
                    s += ' LIMIT ' + str(MAX_LINES['RSAM'])
                except KeyError:
                    pass
                data = db.session.execute(text(s), params=dict(st=date_to_j2k(start, tz), et=date_to_j2k(end, tz),
                                            dsint=interval)).fetchall()
            elif args['downsample'] == 'mean':
                q_items  = []
                interval = args['dsint']
                groupby  = ['intNum', cname.timestamp]
                q_items.append(func.min(cname.timestamp).label('timestamp'))
                q_items.append(func.avg(cname.rsam).label('rsam'))
                q_items.append(((cname.timestamp)-date_to_j2k(start, tz)).self_group().op('div')(interval).label('intNum'))
                q = db.session.query(*q_items).filter(*queryclauses).order_by(*orderby).group_by(*groupby)
                try:
                    q = q.limit(MAX_LINES['RSAM'])
                except KeyError:
                    pass
                data = q.all()

            output[channel] = []
            Date            = j2k_to_date
            List            = output[channel].append
            for d in data:
                List({ 'date': Date(d.timestamp, tz).strftime('%Y-%m-%d %H:%M:%S.%f'), 'rsam': d.rsam })

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
        params['channel'] = {'type': 'string', 'required': 'no', 'note': 'Can be comma-separated list.',
                             'options': rsam._tablenames}
        params['starttime'] = {'type': 'string', 'required': 'yes',
                              'note': 'Will also accept things like -6m for last six months.',
                              'format': 'yyyy[MMdd[hhmm]]'}
        params['endtime'] = {'type': 'string', 'required': 'no', 'format': 'yyyy[MMdd[hhmm]]', 'default': 'now'}
        params['timezone'] = {'type': 'string', 'required': 'no', 'default': 'hst'}
        params['downsample'] = {'type': 'string', 'required': 'no', 'default': 'none', 'options': DS_OPTIONS}
        params['dsint'] = {'type': 'int', 'required': 'no'}
        return params
