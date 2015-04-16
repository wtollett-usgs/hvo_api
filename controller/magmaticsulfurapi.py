from flask import request, current_app
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import settings as json_settings
from model import magmaticsulfur
from sqlalchemy import func
from valverest.database import db4 as db
from valverest.util import clean_input, j2k_to_date, create_date_from_input, date_to_j2k

import json
import logging

class MagmaticSulfurAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('op', type = str, required = False)
        self.reqparse.add_argument('channel', type = str, required = False)
        self.reqparse.add_argument('starttime', type = str, required = False)
        self.reqparse.add_argument('endtime', type = str, required = False, default='now')
        self.reqparse.add_argument('timezone', type = str, required = False, default = 'hst')
        super(MagmaticSulfurAPI, self).__init__()

    def get(self):
        # Return expected parameter output, also set indent settings
        if not request.args:
            return self.create_param_string(), 200

        if (not current_app.debug) and (json_settings and json_settings['indent']):
            json_settings['indent'] = None

        args = self.reqparse.parse_args()
        if 'op' in args and args['op'] == 'time':
            kerz = db.session.query(func.max(magmaticsulfur.KERZ.timestamp)).one()[0]
            hmm  = db.session.query(func.max(magmaticsulfur.HMM.timestamp)).one()[0]
            return { 'KERZ': j2k_to_date(kerz, True).strftime("%Y-%m-%d %H:%M:%S.%f") if kerz else '',
                     'HMM': j2k_to_date(hmm, True).strftime("%Y-%m-%d %H:%M:%S.%f") if hmm else ''}, 200
        else:
            channels  = args['channel'].split(',')
            starttime = args['starttime']
            endtime   = args['endtime']
            tz        = (args['timezone'].lower() == 'hst')
            sd,ed     = create_date_from_input(starttime, endtime, tz)
            jsd       = date_to_j2k(sd, tz)
            jed       = date_to_j2k(ed, tz)
            output    = {}
            count     = 0
            for channel in channels:
                stn  = getattr(magmaticsulfur, channel.upper())
                ob   = [stn.timestamp.desc()]
                data = stn.query.filter(stn.timestamp.between(jsd, jed)).order_by(*ob).all()
                out  = []
                Date = j2k_to_date
                List = out.append
                count += len(data)
                for d in data:
                    List({ 'date': Date(d.timestamp, tz).strftime('%Y-%m-%d %H:%M:%S.%f'),
                            'olvinc_sppm':  d.olvinc_sppm,
                            'sid':          d.sid })
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
                cname = getattr(magmaticsulfur, tbl.upper())
                d     = date_to_j2k(arg['date'], False)
                item  = cname.query.filter_by(timestamp = d).first()
                if item:
                    lf.debug('Updating item with j2ksec: ' + str(d))
                    item.olvinc_sppm = '%.2f' % float(arg['olvinc_sppm']) if arg['olvinc_sppm'] != '' else None
                else:
                    item  = cname(time=arg['date'], olvinc_sppm=arg['olvinc_sppm'], sid=arg['sid'])
                    lf.debug('Attempting to insert magmaticsulfur observation for region=%s, date=%s, olvinc_sppm=%s, '\
                             'sid=%s'
                             % (arg['region'], arg['date'], arg['olvinc_sppm'], arg['sid']))
                    db.session.add(item)
            db.session.commit()
            lf.debug('Item(s) added/Updated')
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
        params['timezone'] = { 'type': 'string', 'required': 'no', 'default': 'hst' }
        params['op'] = { 'type': 'string', 'required': 'no', 'options': 'time',
                         'note': 'Returns datetime for last record in the database. Other parameters not required.'}
        return params
