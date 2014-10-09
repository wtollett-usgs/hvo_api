from flask.ext.restful import Resource
from model import hvologs, cvologs, avologs
from valverest.database import db2 as hvodb, db3 as cvodb, db4 as avodb

import json
import logging

class LogsAPI(Resource):
    def post(self):
        lf = logging.getLogger('file')
        try:
            arg         = json.loads(request.data)
            observatory = arg['db']
            if observatory == 'hvo':
                userobj = getattr(hvologs, 'User')
                cname   = getattr(hvologs, 'Post')
                db      = hvodb
            elif observatory == 'cvo':
                userobj = getattr(cvologs, 'User')
                cname   = getattr(cvologs, 'Post')
                db      = cvodb
            elif observatory == 'avo':
                userobj = getattr(avologs, 'User')
                cname   = getattr(avologs, 'Post')
                db      = avodb

            user = userobj.query.filter_by(username = arg['user']).first()
            item = cname(user.id, arg['date'], arg['subject'], arg['text'], arg['user'])
            lf.debug('Attempting to insert log entry for observatory=%s, date=%s, user=%s, subject=%s, text=%s'
                    % (observatory, arg['date'], arg['user'], arg['subject'], arg['text']))
            db.session.add(item)
            db.session.commit()
            lf.debug('Item added')
            return { 'status': 'ok' }, 201
        except:
            return { 'status': 'error' }, 400
