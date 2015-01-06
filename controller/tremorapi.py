from flask import request, current_app
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import settings as json_settings
from model.tremor import catalog
from valverest.database import db
from valverest.util import create_date_from_input

class TremorAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('methodid', type = int, required = True)
        self.reqparse.add_argument('starttime', type = str, required = True)
        self.reqparse.add_argument('endtime', type = str, required = True)
        self.reqparse.add_argument('region', type = str, required = False, default = 'All')
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
        region    = args['region']
        sd,ed     = create_date_from_input(starttime, endtime)

        data      = catalog.query.filter(catalog.starttime.between(sd, ed), catalog.methodid == methodid, catalog.region==region, catalog.iseq==0).order_by(catalog.starttime.desc()).all()
        output    = []
        List      = output.append
        for d in data:
            List({ 'starttime': d.starttime.strftime("%Y-%m-%d %H:%M:%S.%f"),
                   'latitude':float(d.latitude),
                   'longitude':float(d.longitude),
                   'depth':float(d.depth),
                   'iseq':d.iseq,
                   'evid':d.evid,
                   'methodid': d.methodid,
                   'region': d.region })
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
        params['endtime'] = { 'type': 'string', 'required': 'yes', 'format': 'yyyy[MMdd[hhmm]]'}
        params['methodid'] = { 'type': 'integer', 'required': 'yes', 'note': ''}
        params['region'] = {'type': 'string', 'required': 'no', 'default': 'All'}
        return params
