from datetime import datetime
from flask import request, current_app
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import settings as json_settings
from json import loads as jsonload
from logging import getLogger
from model import hvologs, cvologs, avologs
from valverest.database import db2 as hvodb, db3 as cvodb, db4 as avodb

class LogsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('op', type = str, required = False, default = 'time')
        self.reqparse.add_argument('observatory', type = str, required = False, default = 'hvo')
        super(LogsAPI, self).__init__()

    def get(self):
        # Return expected parameter output, also set indent settings
        if not request.args:
            return self.create_param_string(), 200

        if (not current_app.debug) and (json_settings and json_settings['indent']):
            json_settings['indent'] = None

        args = self.reqparse.parse_args()
        if 'op' in args and args['op'] == 'time':
            obs = args['observatory'].lower()
            if obs == 'avo':
                cname = avologs
                db    = avodb
            elif obs == 'cvo':
                cname = cvologs
                db    = cvodb
            elif obs == 'hvo':
                cname = hvologs
                db    = hvodb

            post = cname.Post.query.order_by(cname.Post.observtime.desc()).first()
            return { 'id': post.obsID, 'observtime': post.observtime.strftime("%Y-%m-%d %H:%M:%S"),
                     'obsdate': post.obsdate.strftime("%Y-%m-%d %H:%M:%S") }, 200

    def post(self):
        lf = getLogger('file')
        try:
            arg         = jsonload(request.data)
            observatory = arg['db'].lower()
            if observatory == 'hvo':
                cname = hvologs
                db    = hvodb
            elif observatory == 'cvo':
                cname = cvologs
                db    = cvodb
            elif observatory == 'avo':
                cname = avologs
                db    = avodb

            pdate    = datetime.strptime(arg['postdate'], '%m/%d/%Y %H:%M:%S')
            odate    = datetime.strptime(arg['obsdate'], '%m/%d/%Y %H:%M:%S')
            user     = cname.User.query.filter_by(email = arg['user']).first()
            item     = cname.Post(user.id, pdate, odate, arg['subject'], arg['text'], user.username)
            volcname = cname.ListVolc.query.filter_by(Volcano = arg['volcano']).first()
            volc     = cname.Volcano.query.filter_by(volcano_name = arg['volcano']).first()
            lf.debug(s = ('Attempting to insert log entry for observatory=%s, postdate=%s, obsdate=%s, user=%s, '
                          'subject=%s, text=%s')
                    % (observatory, arg['postdate'], arg['obsdate'], arg['user'], arg['subject'], arg['text']))
            db.session.add(item)
            db.session.commit()
            linkitem = cname.VolcLink(volcname.VolcNameID, item.obsID, volc.volcano_id)
            lf.debug('Attempting to insert obs/volcano link for VolcNameID=%s, obsID=%s, volcano_id=%s'
                    % (volcname.VolcNameID, item.obsID, volc.volcano_id))
            db.session.add(linkitem)
            db.session.commit()
            lf.debug('Items added')
            return { 'status': 'ok' }, 201
        except:
            return { 'status': 'error' }, 400

    @staticmethod
    def create_param_string():
        if not current_app.debug:
            json_settings['indent']    = 4
            json_settings['sort_keys'] = True

        params = {}
        params['observatory'] = { 'type': 'string', 'required': 'no', 'options': 'avo, cvo, hvo', 'default': 'hvo' }
        params['op'] = { 'type': 'string', 'required': 'no', 'options': 'time',
                         'note': 'Returns datetime for last record in the database. Other parameters not required.'}
        return params
