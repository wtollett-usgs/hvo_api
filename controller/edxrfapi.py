from flask import request, current_app
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import settings as json_settings
from model import edxrf
from sqlalchemy import func
from valverest.database import db
from valverest.util import clean_input, j2k_to_date, create_date_from_input, date_to_j2k

import json
import logging

class EDXRFAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('op', type = str, required = False)
        self.reqparse.add_argument('channel', type = str, required = False)
        self.reqparse.add_argument('starttime', type = str, required = False)
        self.reqparse.add_argument('endtime', type = str, required = False, default='now')
        self.reqparse.add_argument('timezone', type = str, required = False, default = 'hst')
        super(EDXRFAPI, self).__init__()

    def get(self):
        # Return expected parameter output, also set indent settings
        if not request.args:
            return self.create_param_string(), 200

        if (not current_app.debug) and (json_settings and json_settings['indent']):
            json_settings['indent'] = None

        args = self.reqparse.parse_args()
        if 'op' in args and args['op'] == 'time':
            kierz = db.session.query(func.max(edxrf.KIERZ.timestamp)).one()[0]
            kisum = db.session.query(func.max(edxrf.KISUM.timestamp)).one()[0]
            return { 'kierz': j2k_to_date(kierz, False).strftime("%Y-%m-%d %H:%M:%S.%f"),
                     'kisum': j2k_to_date(kisum, False).strftime("%Y-%m-%d %H:%M:%S.%f") }, 200
        else:
            channels     = args['channel'].split(',')
            starttime    = args['starttime']
            endtime      = args['endtime']
            tz           = (args['timezone'].lower() == 'hst')
            sd,ed        = create_date_from_input(starttime, endtime, tz)
            jsd          = date_to_j2k(sd, tz)
            jed          = date_to_j2k(ed, tz)
            queryclauses = []
            output       = {}
            count        = 0
            for channel in channels:
                stn  = getattr(edxrf, channel.upper())
                ob   = [stn.timestamp.desc()]
                data = stn.query.filter(stn.timestamp.between(jsd, jed)).order_by(*ob).all()
                out  = []
                Date = j2k_to_date
                List = out.append
                count += len(data)
                for d in data:
                    List({ 'date': Date(d.timestamp, tz).strftime('%Y-%m-%d %H:%M:%S.%f'),
                            'rb': d.rb,
                            'sr': d.sr,
                            'y': d.y,
                            'zr': d.zr,
                            'nb': d.nb })
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
                cname = getattr(edxrf, tbl.upper())
                d     = date_to_j2k(arg['date'], False)
                item  = cname.query.filter_by(timestamp = d).first()
                if item:
                    lf.debug('Updating item for j2ksec: ' + str(d))
                    item.rb = '%.2f' % float(arg['rb']) if arg['rb'] != '' else None
                    item.sr = '%.2f' % float(arg['sr']) if arg['sr'] != '' else None
                    item.y  = '%.2f' % float(arg['y']) if arg['y'] != '' else None
                    item.zr = '%.2f' % float(arg['zr']) if arg['zr'] != '' else None
                    item.nb = '%.2f' % float(arg['nb']) if arg['nb'] != '' else None
                else:
                    item  = cname(time=arg['date'], rb=arg['rb'], sr=arg['sr'], y=arg['y'], zr=arg['zr'], nb=arg['nb'])
                    lf.debug('Attempting to insert edxrf observation for region=%s, date=%s, rb=%s, sr=%s, y=%s, zr=%s, nb=%s'
                            % (arg['region'], arg['date'], arg['rb'], arg['sr'], arg['y'], arg['zr'], arg['nb']))
                    db.session.add(item)
            db.session.commit()
            lf.debug('Item added')
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
                              'options': 'KIERZ, KISUM' }
        params['starttime'] = { 'type': 'string', 'required': 'yes',
                                'note': 'Will also accept things like -6m for last 6 months.',
                                'format': 'yyyy[MMdd[hhmm]]' }
        params['endtime'] = { 'type': 'string', 'required': 'no', 'format': 'yyyy[MMdd[hhmm]]', 'default': 'now' }
        params['timezone'] = { 'type': 'string', 'required': 'no', 'default': 'hst' }
        params['op'] = { 'type': 'string', 'required': 'no', 'options': 'time',
                         'note': 'Returns datetime for last record in the database. Other parameters not required.'}
        return params
