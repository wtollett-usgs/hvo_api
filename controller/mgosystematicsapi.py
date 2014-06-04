from flask import request, current_app
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import settings as json_settings
from model import mgosystematics
from sqlalchemy import func
from valverest.database import db2 as db
from valverest.util import j2k_to_date, create_date_from_input, date_to_j2k

import json
import logging

class MgOSystematicsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('op', type = str, required = False)
        self.reqparse.add_argument('channel', type = str, required = False)
        self.reqparse.add_argument('starttime', type = str, required = False)
        self.reqparse.add_argument('endtime', type = str, required = False, default='now')
        self.reqparse.add_argument('tz', type = str, required = False, default='HST')
        super(MgOSystematicsAPI, self).__init__()
    
    def get(self):
        # Return expected parameter output, also set indent settings
        if not request.args:
            return self.create_param_string(), 200
            
        if (not current_app.debug) and (json_settings and json_settings['indent']):
            json_settings['indent'] = None
            
        args = self.reqparse.parse_args()
        if 'op' in args and args['op'] == 'time':
            kerz = db.session.query(func.max(mgosystematics.KERZ.timestamp)).one()[0]
            hmm  = db.session.query(func.max(mgosystematics.HMM.timestamp)).one()[0]
            return { 'KERZ': j2k_to_date(kerz, True).strftime("%Y-%m-%d %H:%M:%S.%f") if kerz else '', 
                     'HMM': j2k_to_date(hmm, True).strftime("%Y-%m-%d %H:%M:%S.%f") if hmm else ''}, 200
        elif 'op' in args and args['op'] == 'lastfo':
            t    = mgosystematics.KERZ
            kerz = db.session.query(func.max(t.timestamp)).filter(t.olv_fo_meas != None).one()[0]
            t    = mgosystematics.HMM
            hmm  = db.session.query(func.max(t.timestamp)).filter(t.olv_fo_meas != None).one()[0]
            return { 'KERZ': j2k_to_date(kerz, True).strftime("%Y-%m-%d %H:%M:%S.%f") if kerz else '', 
                     'HMM': j2k_to_date(hmm, True).strftime("%Y-%m-%d %H:%M:%S.%f") if hmm else ''}, 200
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
                stn  = getattr(mgosystematics, channel.upper())
                ob   = [stn.timestamp.desc()]
                data = stn.query.filter(stn.timestamp.between(jsd, jed)).order_by(*ob).all()
                out  = []
                Date = j2k_to_date
                List = out.append
                count += len(data)
                for d in data:
                    List({ 'date': Date(d.timestamp, (args['tz'] == 'HST')).strftime('%Y-%m-%d %H:%M:%S.%f'), 
                            'wr_mgo_wt':        d.wr_mgo_wt,
                            'gls_mgo_wt':       d.gls_mgo_wt,
                            'gls_mgo_tempcorr': d.gls_mgo_tempcorr,
                            'wr_mgo_temp':      d.wr_mgo_temp,
                            'wr_fo_clc':        d.wr_fo_clc,
                            'gls_fo_clccorr':   d.gls_fo_clccorr,
                            'olv_fo_meas':      d.olv_fo_meas,
                            'sid':              d.sid })
                output[channel] = out
            return { 'nr': count, 
                     'records': output }, 200
        
    def post(self):
        lf = logging.getLogger('file')
        try:
            args  = json.loads(request.data)
            for arg in args:
                tbl   = arg['region']
                cname = getattr(mgosystematics, tbl.upper())
                if 'type' in arg and arg['type'] == 'fo':
                    d    = date_to_j2k(arg['date'], False)
                    item = cname.query.filter_by(timestamp = d).first()
                    if item:
                        lf.debug('Updating item with j2ksec: ' + str(d))
                        item.olv_fo_meas = '%.2f' % float(arg['olv_fo_meas'])
                    else:
                        lf.debug('Inserting new item for j2ksec: ' + str(d))
                        item = cname(time=arg['date'], olv_fo_meas=arg['olv_fo_meas'], sid=arg['sid'])
                        db.session.add(item)
                else:
                    item  = cname(time=arg['date'], wr_mgo_wt=arg['wr_mgo_wt'], gls_mgo_wt=arg['gls_mgo_wt'], 
                                  gls_mgo_tempcorr=arg['gls_mgo_tempcorr'], wr_mgo_temp=arg['wr_mgo_temp'], 
                                  wr_fo_clc=arg['wr_fo_clc'], gls_fo_clccorr=arg['gls_fo_clccorr'], 
                                  olv_fo_meas=arg['olv_fo_meas'], sid=arg['sid'])
                    lf.debug('Attempting to insert mgosystematics observation for region=%s, date=%s, wr_mgo_wt=%s, '\
                             'gls_mgo_wt=%s, gls_mgo_tempcorr=%s, wr_mgo_temp=%s, wr_fo_clc=%s, gls_fo_clccorr=%s, '\
                             'olv_fo_meas=%s, sid=%s'
                            % (arg['region'], arg['date'], arg['wr_mgo_wt'], arg['gls_mgo_wt'], arg['gls_mgo_tempcorr'], 
                               arg['wr_mgo_temp'], arg['wr_fo_clc'], arg['gls_fo_clccorr'], arg['olv_fo_meas'], 
                               arg['sid']))
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