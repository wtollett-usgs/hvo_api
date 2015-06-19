from datetime import datetime
from flask import request, current_app
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import settings as json_settings
from json import loads as jsonload
from logging import getLogger
from model import hvologs
from valverest.database import db2 as hvodb

import traceback

class LogsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('op', type = str, required = False, default = 'time')
        self.reqparse.add_argument('num', type = int, required = False, default = 20)
        super(LogsAPI, self).__init__()

    def get(self):
        # Return expected parameter output, also set indent settings
        if not request.args:
            return self.create_param_string(), 200

        if (not current_app.debug) and (json_settings and json_settings['indent']):
            json_settings['indent'] = None

        output = []
        args   = self.reqparse.parse_args()
        cname  = hvologs
        db     = hvodb

        if 'op' in args and args['op'] == 'time':
            post = cname.Post.query.order_by(cname.Post.observtime.desc()).first()
            return { 'id': post.obsID, 'observtime': post.observtime.strftime("%Y-%m-%d %H:%M:%S"),
                     'obsdate': post.obsdate.strftime("%Y-%m-%d %H:%M:%S") }, 200
        else:
            posts  = cname.Post.query.order_by(cname.Post.sortdate.desc()).limit(args['num']).all()
            output = map(self.create_data_map, posts)
            return { 'nr': len(posts), 'posts': output }, 200

    def post(self):
        lf = getLogger('file')
        try:
            arg         = jsonload(request.data)
            observatory = arg['db'].lower()
            cname       = hvologs
            db          = hvodb

            # Is this an edit of a previous item?
            item = cname.Post.query.filter_by(subject = arg['subject']).first()
            if item:
                lf.debug('Updating item with subject: %s' % arg['subject'])
                item.obstext = arg['text']
                user         = cname.User.query.filter_by(email = arg['user']).first()
                if user and item.userID != user.id:
                    item.userID = user.id
                db.session.commit()
            else:
                pdate = datetime.strptime(arg['postdate'], '%Y-%m-%d %H:%M')
                odate = datetime.strptime(arg['obsdate'], '%Y-%m-%d %H:%M:%S')
                user  = cname.User.query.filter_by(email = arg['user']).first()
                if user:
                    item = cname.Post(user.id, pdate, odate, arg['subject'], arg['text'], user.username)
                else:
                    item = cname.Post(0, pdate, odate, arg['subject'], arg['text'], '')
                s = 'Attempting to insert log entry for postdate=%s, obsdate=%s, user=%s, subject=%s'
                lf.debug(s % (arg['postdate'], arg['obsdate'], arg['user'], arg['subject']))
                db.session.add(item)
                db.session.commit()

                # Find volnames and volc_ids
                volcanoes = arg['volcano'].split(',')
                volcname  = []
                volc      = []
                for v in volcanoes:
                    volcname.append(cname.ListVolc.query.filter_by(Volcano = v).first())
                    volc.append(cname.Volcano.query.filter_by(volcano_name = v).first())

                # Insert volcano links
                for i in range(len(volcanoes)):
                    linkitem = cname.VolcLink(volcname[i].VolcNameID, item.obsID, volc[i].volcano_id)
                    lf.debug('Attempting to insert obs/volcano link for VolcNameID=%s, obsID=%s, volcano_id=%s'
                            % (volcname[i].VolcNameID, item.obsID, volc[i].volcano_id))
                    db.session.add(linkitem)
                db.session.commit()
                lf.debug('Items added')

                # Insert 'Earthquake' tag link
                tagitem = cname.KeywordLink(item.obsID)
                lf.debug('Attempting to insert obs/keyword link for obsID=%s, keywordid=23' % item.obsID)
                db.session.add(tagitem)
                db.session.commit()
                lf.debug('Item added')

                # Add item to the ignore list
                igitem = cname.Ignore(item.subject)
                lf.debug('Attempting to insert item in ignore list for subject=%s' % item.subject)
                db.session.add(igitem)
                db.session.commit()
                lf.debug('Item added')

            return { 'status': 'ok' }, 201
        except Exception:
            lf.debug(traceback.format_exc())
            return { 'status': 'error' }, 400

    @staticmethod
    def create_data_map(data):
        item = {}
        item['title'] = data.subject
        item['text'] = data.obstext
        item['user'] = data.user.username
        item['postdate'] = data.observtime.strftime('%Y-%m-%d %H:%M:%S.%f')
        item['sortdate'] = data.sortdate.strftime('%Y-%m-%d %H:%M:%S.%f')

        return item

    @staticmethod
    def create_param_string():
        if not current_app.debug:
            json_settings['indent']    = 4
            json_settings['sort_keys'] = True

        params = {}
        params['op'] = { 'type': 'string', 'required': 'no', 'options': 'time, posts',
                         'note': 'Returns datetime for last record in the database. Other parameters not required.'}
        params['num'] = { 'type': 'int', 'required': 'no', 'default': 20, 'note': 'Number of log entries to return'}
        return params
