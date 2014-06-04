from flask import request, current_app
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import settings as json_settings
from model import incompatibles
from sqlalchemy import func
from valverest.database import db3 as db
from valverest.util import j2k_to_date, create_date_from_input, date_to_j2k

import json
import logging

class IncompatiblesAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('op', type = str, required = False)
        self.reqparse.add_argument('channel', type = str, required = False)
        self.reqparse.add_argument('starttime', type = str, required = False)
        self.reqparse.add_argument('endtime', type = str, required = False, default='now')
        self.reqparse.add_argument('tz', type = str, required = False, default='HST')
        super(IncompatiblesAPI, self).__init__()
    
    def get(self):
        # Return expected parameter output, also set indent settings
        if not request.args:
            return self.create_param_string(), 200
            
        if (not current_app.debug) and (json_settings and json_settings['indent']):
            json_settings['indent'] = None
            
        args = self.reqparse.parse_args()
        if 'op' in args and args['op'] == 'time':
            kerz = db.session.query(func.max(incompatibles.KERZ.timestamp)).one()[0]
            hmm  = db.session.query(func.max(incompatibles.HMM.timestamp)).one()[0]
            return { 'KERZ': j2k_to_date(kerz, True).strftime("%Y-%m-%d %H:%M:%S.%f") if kerz else '', 
                     'HMM': j2k_to_date(hmm, True).strftime("%Y-%m-%d %H:%M:%S.%f") if hmm else '' }, 200
        else:
            channels  = args['channel'].split(',')
            starttime = args['starttime']
            endtime   = args['endtime']
            sd,ed     = create_date_from_input(starttime, endtime)
            jsd       = date_to_j2k(sd, (args['tz'] == 'HST'))
            jed       = date_to_j2k(ed, (args['tz'] == 'HST'))
            output    = {}
            count     = 0
            for channel in channels:
                stn  = getattr(incompatibles, channel.upper())
                ob   = [stn.timestamp.desc()]
                data = stn.query.filter(stn.timestamp.between(jsd, jed)).order_by(*ob).all()
                out  = []
                Date = j2k_to_date
                List = out.append
                count += len(data)
                for d in data:
                    List({ 'date': Date(d.timestamp, (args['tz'] == 'HST')).strftime('%Y-%m-%d %H:%M:%S.%f'), 
                            'wr_k2o_tio2':   d.wr_k2o_tio2,
                            'gls_k2o_tio2':  d.gls_k2o_tio2,
                            'wr_cao_al2o3':  d.wr_cao_al2o3,
                            'wr_cao_tio2':   d.wr_cao_tio2,
                            'wr_la_yb_inaa': d.wr_la_yb_inaa,
                            'wr_zr_y_wdx':   d.wr_zr_y_wdx,
                            'wr_zr_y_edx':   d.wr_zr_y_edx,
                            'wr_sr_edx':     d.wr_sr_edx,
                            'sid':           d.sid })
                output[channel] = out
            return { 'nr': count, 
                     'records': output }, 200
        
    def post(self):
        lf = logging.getLogger('file')
        try:
            args = json.loads(request.data)
            for arg in args:
                tbl   = arg['region']
                cname = getattr(incompatibles, tbl.upper())
                item  = cname(time=arg['date'], wr_k2o_tio2=arg['wr_k2o_tio2'], gls_k2o_tio2=arg['gls_k2o_tio2'], 
                              wr_cao_al2o3=arg['wr_cao_al2o3'], wr_cao_tio2=arg['wr_cao_tio2'], 
                              wr_la_yb_inaa=arg['wr_la_yb_inaa'], wr_zr_y_wdx=arg['wr_zr_y_wdx'], 
                              wr_zr_y_edx=arg['wr_zr_y_edx'], wr_sr_edx=arg['wr_sr_edx'], sid=arg['sid'])
                lf.debug('Attempting to insert incompatibles observation for region=%s, date=%s, wr_k2o_tio2=%s, '\
                         'gls_k2o_tio2=%s, wr_cao_al2o3=%s, wr_cao_tio2=%s, wr_la_yb_inaa=%s, wr_zr_y_wdx=%s, '\
                         'wr_zr_y_edx=%s, wr_sr_edx=%s, sid=%s'
                        % (arg['region'], arg['date'], arg['wr_k2o_tio2'], arg['gls_k2o_tio2'], arg['wr_cao_al2o3'], 
                           arg['wr_cao_tio2'], arg['wr_la_yb_inaa'], arg['wr_zr_y_wdx'], arg['wr_zr_y_edx'], 
                           arg['wr_sr_edx'], arg['sid']))
                db.session.add(item)
            db.session.commit()
            lf.debug('Item(s) added')
            return { 'status': 'ok' }, 201 
        except:
            return { 'status': 'error' }, 400
            
    @staticmethod
    def create_param_string():
        if not current_app.debug:
            json_settings['indent']    = 4
            json_settings['sort_keys'] = True
            
        params = {}
        params['channel'] = { 'type': 'string', 'required': 'yes', 'note': 'can be comma-separated list.', 
                              'options': 'KERZ, HMM' }
        params['starttime'] = { 'type': 'string', 'required': 'yes', 
                                'note': 'Will also accept things like -6m for last 6 months.', 
                                'format': 'yyyy[MMdd[hhmm]]' }
        params['endtime'] = { 'type': 'string', 'required': 'no', 'format': 'yyyy[MMdd[hhmm]]', 'default': 'now' }
        params['tz'] = { 'type': 'string', 'required': 'no', 'default': 'HST' }
        params['op'] = { 'type': 'string', 'required': 'no', 'options': 'time', 
                         'note': 'Returns datetime for last record in the database. Other parameters not required.'}
        return params
