from flask import request
from flask.ext.restful import Resource
from model import hvologs, cvologs, avologs
from valverest.database import db2 as hvodb, db3 as cvodb, db4 as avodb

import json
import logging

class LogsAPI(Resource):
    def post(self):
        lf = logging.getLogger('file')
        print "In Post()"
        try:
            arg         = json.loads(request.data)
            observatory = arg['db']
            if observatory == 'hvo':
                cname = hvologs
                db    = hvodb
            elif observatory == 'cvo':
                cname = cvologs
                db    = cvodb
            elif observatory == 'avo':
                cname = avologs
                db    = avodb

            user     = cname.User.query.filter_by(username = arg['user']).first()
            item     = cname.Post(user.id, arg['date'], arg['subject'], arg['text'], arg['user'])
            volcname = cname.ListVolc.query.filter_by(Volcano = arg['volcano']).first()
            volc     = cname.Volcano.query.filter_by(volcano_name = arg['volcano']).first()
            lf.debug('Attempting to insert log entry for observatory=%s, date=%s, user=%s, subject=%s, text=%s'
                    % (observatory, arg['date'], arg['user'], arg['subject'], arg['text']))
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
