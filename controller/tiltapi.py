from common_constants import MAX_LINES, DS_OPTIONS
from flask import request, current_app
from flask_restful import Resource, reqparse
from math import cos, sin, radians, sqrt, atan2
from numpy import empty, insert, matrix
from sqlalchemy import func
from sqlalchemy.sql import text
from sys import float_info
from valverest.database import db2 as db
from valverest.util import create_date_from_input, date_to_j2k, j2k_to_date, str_to_date

import model.tilt as tilt

_series_options  = ['all', 'radial', 'tangential', 'east', 'north', 'magnitude', 'azimuth',
                    'holeTemp', 'boxTemp', 'instVolt', 'rainfall']
_azimuth_options = ['nominal', 'optimal', 'user-defined float value']

class TiltAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('channel', type = str, required = True)
        self.reqparse.add_argument('rank', type = int, required = False, default = 1)
        self.reqparse.add_argument('series', type = str, required = False, default = 'radial,tangential')
        self.reqparse.add_argument('starttime', type = str, required = True)
        self.reqparse.add_argument('endtime', type = str, required = False, default = 'now')
        self.reqparse.add_argument('timezone', type = str, required = False, default = 'hst')
        self.reqparse.add_argument('azimuth', type = str, required = False, default = 'nominal')
        self.reqparse.add_argument('downsample', type = str, required = False, default = 'none')
        self.reqparse.add_argument('dsint', type = int, required = False)
        super(TiltAPI, self).__init__()

    def get(self):
        if not request.args:
            return self.create_param_string(), 200

        if not current_app.debug:
            current_app.config['RESTFUL_JSON'] = {}

        args = self.reqparse.parse_args()

        # Check that valid channels were queried
        channels = args['channel'].split(',')
        unknown  = set([x.upper() for x in channels]).difference(tilt._tablenames)
        if len(unknown) > 0:
            return { 'Error': 'unknown channel: %s' % ','.join(unknown)}

        # Timezone
        tz = (args['timezone'] == 'hst')

        # Start by getting all the data
        start, end = create_date_from_input(args['starttime'], args['endtime'], tz)
        raw_output = {}
        count      = 0

        # If we're downsampling, we need to create the query by hand
        for channel in channels:
            cname        = getattr(tilt, channel.upper())
            queryclauses = []
            orderby      = []

            # Set up query filters
            queryclauses.append(cname.timestamp.between(date_to_j2k(start, tz), date_to_j2k(end, tz)))

            # Set up orderby clauses
            orderby.append(cname.timestamp.asc())

            if args['rank'] == 0:
                orderby.append(cname.rid.desc())
            else:
                queryclauses.append(cname.rid == args['rank'])

            if args['downsample'] == 'none':
                # Query the data and map it to the raw_tilt_fields structure
                q_items = []
                q_items.extend([cname.timestamp.label('timestamp'), cname.rid.label('rid')])
                q_items.append((func.cos(func.radians(tilt.TiltTranslation.azimuth)) * (cname.xTilt * \
                                tilt.TiltTranslation.cxTilt + tilt.TiltTranslation.dxTilt).self_group() + \
                                func.sin(func.radians(tilt.TiltTranslation.azimuth)) * (cname.yTilt * \
                                tilt.TiltTranslation.cyTilt + tilt.TiltTranslation.dyTilt).self_group()).label('east'))
                q_items.append((-func.sin(func.radians(tilt.TiltTranslation.azimuth)) * (cname.xTilt * \
                                tilt.TiltTranslation.cxTilt + tilt.TiltTranslation.dxTilt).self_group() + \
                                func.cos(func.radians(tilt.TiltTranslation.azimuth)) * (cname.yTilt * \
                                tilt.TiltTranslation.cyTilt + tilt.TiltTranslation.dyTilt).self_group()).label('north'))
                q_items.extend([tilt.TiltRank.name, tilt.TiltTranslation])

                # Add optional parameters
                tt = tilt.TiltTranslation
                if any(x in args['series'] for x in ['holeTemp', 'all']):
                    q_items.append((cname.holeTemp * tt.choleTemp + tt.dholeTemp).label('holeTemp'))
                if any(x in args['series'] for x in ['boxTemp', 'all']):
                    q_items.append((cname.boxTemp * tt.cboxTemp + tt.dboxTemp).label('boxTemp'))
                if any(x in args['series'] for x in ['instVolt', 'all']):
                    q_items.append((cname.instVolt * tt.cinstVolt + tt.dinstVolt).label('instVolt'))
                if any(x in args['series'] for x in ['rainfall', 'all']):
                    q_items.append((cname.rainfall * tt.crainfall + tt.drainfall).label('rainfall'))

                q = db.session.query(*q_items).join(tilt.TiltTranslation, tilt.TiltRank)
                q = q.filter(*queryclauses).order_by(*orderby)
                try:
                    q = q.limit(MAX_LINES['TILT'])
                except KeyError:
                    pass
                data = q.all()

                data = self.filter_nulls(data)

                raw_output[channel] = map(self.create_initial_output, data)

                # Adjust dates from j2ksec to actual datetime
                for d in raw_output[channel]:
                    d['date'] = j2k_to_date(d['date'], tz).strftime('%Y-%m-%d %H:%M:%S.%f')
            elif args['downsample'] == 'decimate':
                interval = int(args['dsint'])
                dbname   = 'v3_hvo_deformation_tilt$tilt'
                s        = "SELECT * FROM(SELECT fullquery.*, @row := @row+1 AS rownum "\
                            "FROM (SELECT j2ksec as timestamp, c.rid, c.name, COS(RADIANS(b.azimuth)) * "\
                            "(xTilt * cxTilt + dxTilt) + SIN(RADIANS(b.azimuth)) * (yTilt * cyTilt + "\
                            "dyTilt) as east, (-SIN(RADIANS(b.azimuth))) * (xTilt * cxTilt + dxTilt) + "\
                            "COS(RADIANS(b.azimuth)) * (yTilt * cyTilt + dyTilt) as north, holeTemp * "\
                            "cHoleTemp + dHoleTemp as holeTemp, boxTemp * cboxTemp + dboxTemp as boxTemp, "\
                            "instVolt * cinstVolt + dinstVolt as instVolt, rainfall * crainfall + "\
                            "drainfall as rainfall FROM " + dbname + "." + cname.__tablename__ + " a INNER "\
                            "JOIN " + dbname + ".translations b on a.tid = b.tid INNER JOIN " + dbname + \
                            ".ranks c ON a.rid = c.rid WHERE j2ksec BETWEEN :st AND :et "
                if args['rank'] != 0:
                    s += "AND c.rid = :rid ORDER BY j2ksec ASC"
                else:
                    s += "ORDER BY j2ksec ASC AND a.rid DESC"
                s += ") fullquery, (SELECT @row:=0) r) ranked WHERE rownum % :dsint = 1"
                try:
                    s += ' LIMIT ' + str(MAX_LINES['TILT'])
                except KeyError:
                    pass
                data = db.session.execute(text(s), params=dict(dsint=interval, st=date_to_j2k(start, tz),
                                            et=date_to_j2k(end, tz), rid=args['rank'])).fetchall()
                data = self.filter_nulls(data)
                raw_output[channel] = map(self.create_initial_output, data)
                for d in raw_output[channel]:
                    d['date'] = j2k_to_date(d['date'], tz).strftime('%Y-%m-%d %H:%M:%S.%f')
            elif args['downsample'] == 'mean':
                pass

            # Calculate rainfall
            if 'rainfall' in args['series'] or 'all' in args['series']:
                lastval = -1
                total   = 0
                for d in raw_output[channel]:
                    if lastval == -1:
                        lastval = d['rainfall']
                        d['rainfall'] = 0
                    elif d['rainfall'] == lastval:
                        d['rainfall'] = total
                    else:
                        total  += d['rainfall'] - lastval
                        lastval = d['rainfall']
                        d['rainfall'] = total
            count += len(data)

        # Now go through and compute things like radial, tangential, azimuth, magnitude if requested by the user
        if set(args['series'].split(',')).intersection(['all', 'radial', 'tangential', 'magnitude', 'azimuth', 'east', 'north']):
            tc = tilt.TiltChannel
            for channel in channels:
                data = raw_output[channel]
                if args['azimuth'] == 'nominal':
                    azimuth = tc.query.filter(tc.code == channel.upper()).first().azimuth % 360.0
                elif args['azimuth'] == 'optimal':
                    azimuth = self.get_optimal_azimuth(data) % 360.0
                else:
                    azimuth = args['azimuth'] % 360.0
                
                if len(data) == 0:
                    continue

                # Subtract means to get zero-based values
                em = sum([x['east'] for x in data]) / len(data)
                nm = sum([x['north'] for x in data]) / len(data)
                for i in data:
                    i['east']  -= em
                    i['north'] -= nm

                tr              = radians(azimuth)
                rotation_matrix = matrix([[cos(tr), sin(tr)], [-sin(tr), cos(tr)]])

                # Add radial, tangential, magnitude, and azimuth vals to output
                ox = data[0]['east']
                oy = data[0]['north']
                for i in data:
                    e, n = i['east'], i['north']
                    m    = matrix([[e, n]]) * rotation_matrix
                    if any(x in args['series'] for x in ['radial', 'all']):
                        i['radial'] = m.A[0][1]
                    if any(x in args['series'] for x in ['tangential', 'all']):
                        i['tangential'] = m.A[0][0]
                    if any(x in args['series'] for x in ['magnitude', 'all']):
                        i['magnitude'] = sqrt((e - ox) * (e - ox) + (n - oy) * (n - oy))
                    if any(x in args['series'] for x in ['azimuth', 'all']):
                        i['azimuth'] = atan2(n - oy, e - ox)

                # If east and/or north aren't in the series list, remove them from output
                if not any(x in args['series'] for x in ['east', 'all']):
                    for d in data:
                        del d['east']
                if not any(x in args['series'] for x in ['north', 'all']):
                    for d in data:
                        del d['north']

        return { 'nr': count,
                 'used_azimuth': azimuth,
                 'tangential_azimuth': (azimuth + 90) % 360,
                 'records': raw_output }, 200

    @staticmethod
    def get_optimal_azimuth(data):
        g              = matrix([[str_to_date(i['date']), 1.0] for i in data])
        ginv           = (g.T * g).I * g.T
        minR, minTheta = float_info.max, 0.0
        theta          = 0
        while theta <= 360.0:
            tr = radians(theta)
            rm = matrix([[cos(tr), sin(tr)], [-sin(tr), cos(tr)]])
            D  = rm * matrix([[i['east'], i['north']] for i in data]).T
            d  = matrix([[D.A[0][x] for x in range(len(D.A[0]))]]).T
            m  = ginv * d
            GM = g * m
            r  = matrix(empty((0,2)))
            for i in range(len(d)):
                r = insert(r, len(r), [d.A[i] - GM.A[i]], axis=0)
            r   = r.T * r
            val = r.A[0][0]
            if val < minR:
                minR     = val
                minTheta = theta
            theta += 1.0
        minTheta = minTheta % 360.0
        minTheta = 360.0 - minTheta
        return minTheta

    @staticmethod
    def create_initial_output(data):
        item          = {}
        item['date']  = data.timestamp
        item['rank']  = data.name
        item['east']  = data.east
        item['north'] = data.north

        if 'holeTemp' in data.keys():
            item['holeTemp'] = data.holeTemp
        if 'boxTemp' in data.keys():
            item['boxTemp'] = data.boxTemp
        if 'instVolt' in data.keys():
            item['instVolt'] = data.instVolt
        if 'rainfall' in data.keys():
            item['rainfall'] = data.rainfall
        return item

    @staticmethod
    def filter_nulls(data):
        d2 = data[:]
        for d in d2:
            if not d.east and not d.north:
                data.remove(d)
        return data

    @staticmethod
    def create_param_string():
        if not current_app.debug:
            settings = current_app.config.get('RESTFUL_JSON', {})
            settings.setdefault('indent', 4)
            settings.setdefault('sort_keys', True)
            current_app.config['RESTFUL_JSON'] = settings

        params = {}
        params['channel'] = {'type': 'string', 'required': 'yes', 'note': 'Can be comma-separated list.',
                            'options': tilt._tablenames}
        params['starttime'] = {'type': 'string', 'required': 'yes',
                              'note': 'Will also accept things like -6m for last six months.',
                              'format': 'yyyy[MMdd[hhmm]]'}
        params['endtime'] = {'type': 'string', 'required': 'no', 'format': 'yyyy[MMdd[hhmm]]', 'default': 'now'}
        params['rank'] = {'type': 'int', 'required': 'no', 'default': 1,
                         'note': 'A rank of 0 will return the best possible rank.'}
        params['timezone'] = {'type': 'string', 'required': 'no', 'default': 'hst'}
        params['series'] = {'type': 'string', 'required': 'no', 'note': 'Can be comma-separated list.',
                            'default': 'radial,tangential', 'options': _series_options}
        params['azimuth'] = {'type': 'string', 'required': 'no', 'default': 'nominal', 'options': _azimuth_options}
        params['downsample'] = {'type': 'string', 'required': 'no', 'default': 'none', 'options': DS_OPTIONS}
        params['dsint'] = {'type': 'int', 'required': 'no'}
        return params
