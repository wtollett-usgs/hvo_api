from flask import request, current_app
from flask_restful import Resource, reqparse
from model import mgosystematics
from sqlalchemy import func
from valverest.database import db2 as db
from valverest.util import clean_input, j2k_to_date, create_date_from_input, date_to_j2k

import json
import logging

class MgOSystematicsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('op', type = str, required = False)
        self.reqparse.add_argument('channel', type = str, required = False)
        self.reqparse.add_argument('starttime', type = str, required = False)
        self.reqparse.add_argument('endtime', type = str, required = False, default='now')
        self.reqparse.add_argument('timezone', type = str, required = False, default = 'hst')
        super(MgOSystematicsAPI, self).__init__()

    def get(self):
        # Return expected parameter output, also set indent settings
        if not request.args:
            return self.create_param_string(), 200

        if not current_app.debug:
            current_app.config['RESTFUL_JSON'] = {}

        args = self.reqparse.parse_args()
        tz   = (args['timezone'].lower() == 'hst')
        if 'op' in args and args['op'] == 'time':
            kerz = db.session.query(func.max(mgosystematics.KERZ.timestamp)).one()[0]
            hmm  = db.session.query(func.max(mgosystematics.HMM.timestamp)).one()[0]
            return { 'KERZ': j2k_to_date(kerz, tz).strftime("%Y-%m-%d %H:%M:%S.%f") if kerz else '',
                     'HMM': j2k_to_date(hmm, tz).strftime("%Y-%m-%d %H:%M:%S.%f") if hmm else ''}, 200
        elif 'op' in args and args['op'] == 'lastfo':
            t    = mgosystematics.KERZ
            kerz = db.session.query(func.max(t.timestamp)).filter(t.olv_fo_meas != None).one()[0]
            t    = mgosystematics.HMM
            hmm  = db.session.query(func.max(t.timestamp)).filter(t.olv_fo_meas != None).one()[0]
            return { 'KERZ': j2k_to_date(kerz, tz).strftime("%Y-%m-%d %H:%M:%S.%f") if kerz else '',
                     'HMM': j2k_to_date(hmm, tz).strftime("%Y-%m-%d %H:%M:%S.%f") if hmm else ''}, 200
        else:
            channels  = args['channel'].split(',')
            starttime = args['starttime']
            endtime   = args['endtime']
            sd,ed     = create_date_from_input(starttime, endtime, tz)
            jsd       = date_to_j2k(sd, tz)
            jed       = date_to_j2k(ed, tz)
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
                    List({ 'date': Date(d.timestamp, tz).strftime('%Y-%m-%d %H:%M:%S.%f'),
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
                arg   = clean_input(arg)
                tbl   = arg['region']
                cname = getattr(mgosystematics, tbl.upper())
                if 'type' in arg and arg['type'] == 'fo':
                    d    = date_to_j2k(arg['date'], False)
                    item = cname.query.filter_by(timestamp = d).first()
                    if item:
                        lf.debug('MGOSYS::Updating item with j2ksec: ' + str(d))
                        item.olv_fo_meas = '%.2f' % float(arg['olv_fo_meas'])
                    else:
                        lf.debug('MGOSYS::Inserting new item for j2ksec: ' + str(d))
                        item = cname(time=arg['date'], olv_fo_meas=arg['olv_fo_meas'], sid=arg['sid'])
                        db.session.add(item)
                else:
                    d    = date_to_j2k(arg['date'], False)
                    item = cname.query.filter_by(timestamp = d).first()
                    if item:
                        lf.debug('MGOSYS::Updating mgosystematics item with j2ksec: ' + str(d))
                        item.wr_mgo_wt        = '%.2f' % float(arg['wr_mgo_wt']) if arg['wr_mgo_wt'] != '' else None
                        item.gls_mgo_wt       = '%.2f' % float(arg['gls_mgo_wt']) if arg['gls_mgo_wt'] != '' else None
                        item.gls_mgo_tempcorr = '%.2f' % float(arg['gls_mgo_tempcorr']) if arg['gls_mgo_tempcorr'] != '' else None
                        item.wr_mgo_temp      = '%.2f' % float(arg['wr_mgo_temp']) if arg['wr_mgo_temp'] != '' else None
                        item.wr_fo_clc        = '%.2f' % float(arg['wr_fo_clc']) if arg['wr_fo_clc'] != '' else None
                        item.gls_fo_clccorr   = '%.2f' % float(arg['gls_fo_clccorr']) if arg['gls_fo_clccorr'] != '' else None
                        item.olv_fo_meas      = '%.2f' % float(arg['olv_fo_meas']) if arg['olv_fo_meas'] != '' else None
                        item.sid              = arg['sid'] if arg['sid'] != '' else None
                    else:
                        lf.debug('MGOSYS::Inserting new mgosystematics item for j2ksec: ' + str(d))
                        item = cname(time=arg['date'], wr_mgo_wt=arg['wr_mgo_wt'], gls_mgo_wt=arg['gls_mgo_wt'],
                                     gls_mgo_tempcorr=arg['gls_mgo_tempcorr'], wr_mgo_temp=arg['wr_mgo_temp'],
                                     wr_fo_clc=arg['wr_fo_clc'], gls_fo_clccorr=arg['gls_fo_clccorr'],
                                     olv_fo_meas=arg['olv_fo_meas'], sid=arg['sid'])
                        lf.debug('MGOSYS::Attempting to insert mgosystematics observation for region=%s, date=%s, wr_mgo_wt=%s, '\
                                 'gls_mgo_wt=%s, gls_mgo_tempcorr=%s, wr_mgo_temp=%s, wr_fo_clc=%s, gls_fo_clccorr=%s, '\
                                 'olv_fo_meas=%s, sid=%s'
                                % (arg['region'], arg['date'], arg['wr_mgo_wt'], arg['gls_mgo_wt'], arg['gls_mgo_tempcorr'],
                                   arg['wr_mgo_temp'], arg['wr_fo_clc'], arg['gls_fo_clccorr'], arg['olv_fo_meas'],
                                   arg['sid']))
                        db.session.add(item)
            db.session.commit()
            lf.debug('MGOSYS::Item(s) added/updated')
            return { 'status': 'ok' }, 201
        except:
            return { 'status': 'error' }, 400

    @staticmethod
    def create_param_string():
        if not current_app.debug:
            settings = current_app.config.get('RESTFUL_JSON', {})
            settings.setdefault('indent', 4)
            settings.setdefault('sort_keys', True)
            current_app.config['RESTFUL_JSON'] = settings

        params = {}
        params['channel'] = { 'type': 'string', 'required': 'yes', 'note': 'can be comma-separated list.',
                              'options': 'KERZ, HMM' }
        params['starttime'] = { 'type': 'string', 'required': 'yes',
                                'note': 'Will also accept things like -6m for last 6 months.',
                                'format': 'yyyy[MMdd[hhmm]]' }
        params['endtime'] = { 'type': 'string', 'required': 'no', 'format': 'yyyy[MMdd[hhmm]]', 'default': 'now' }
        params['timezone'] = { 'type': 'string', 'required': 'no', 'default': 'hst' }
        params['op'] = { 'type': 'string', 'required': 'no', 'options': 'time',
                         'note': 'Returns datetime for last record in the database. Other parameters not required.'}
        return params
