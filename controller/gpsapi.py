from common_constants import MAX_LINES, DS_OPTIONS
from flask import request, current_app
from flask_restful import Resource, reqparse
from math import atan, atan2, cos, degrees, fabs, pow as fpow, radians, sin, sqrt
from model.gps import GPSChannel, GPSSource, GPSRank, GPSDataPoint, Solution
from numpy import zeros, matrix, copyto, concatenate
from sqlalchemy import func
from sqlalchemy.sql import text
from valverest.database import db7 as db
from valverest.util import create_date_from_input, date_to_j2k, j2k_to_date

_series_options = ['east', 'north', 'up', 'length']

class GPSAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('channel', type = str, required = True)
        self.reqparse.add_argument('rank', type = int, required = False, default = 8)
        self.reqparse.add_argument('series', type = str, required = False, default = 'east,north,up')
        self.reqparse.add_argument('starttime', type = str, required = True)
        self.reqparse.add_argument('endtime', type = str, required = False, default = 'now')
        self.reqparse.add_argument('timezone', type = str, required = False, default = 'hst')
        self.reqparse.add_argument('baseline', type = str, required = False)
        self.reqparse.add_argument('downsample', type = str, required = False, default = 'none')
        self.reqparse.add_argument('dsint', type = int, required = False)
        super(GPSAPI, self).__init__()

    def get(self):
        if not request.args:
            return self.create_param_string(), 200

        if not current_app.debug:
            current_app.config['RESTFUL_JSON'] = {}

        args = self.reqparse.parse_args()

        channels = args['channel'].split(',')
        if set([x.upper() for x in channels]).difference([x.code for x in GPSChannel.query.all()]):
           return { 'Error': 'unknown channel' }

        tz         = (args['timezone'] == 'hst')
        start, end = create_date_from_input(args['starttime'], args['endtime'], tz)
        q_data     = {}
        count      = 0
        for channel in channels:
            data  = self.get_gps_data(channel, args, [start, end, tz])
            if len(data) == 0:
                q_data[channel] = []
            else:
                cdata = []

                originllh = self.xyz_to_llh(data['xyz'][0], data['xyz'][1], data['xyz'][2])
                if args['baseline']:
                    bchannel = args['baseline']
                    baseline = self.get_gps_data(bchannel, args, [start, end, tz])
                    data     = self.apply_baseline(baseline, data)

                xyz, cov = self.to_enu(originllh[0], originllh[1], len(data['xyz'])/3, data['xyz'], data['cov'])
                enurows  = self.column_3N_to_rows(xyz)

                em = sum(enurows[x,0] for x in range(len(enurows))) / float(len(enurows))
                nm = sum(enurows[x,1] for x in range(len(enurows))) / float(len(enurows))
                um = sum(enurows[x,2] for x in range(len(enurows))) / float(len(enurows))
                for i in range(len(enurows)):
                    enurows[i,0] -= em
                    enurows[i,1] -= nm
                    enurows[i,2] -= um

                lm = sum(data['lendata'][x] for x in range(len(data['lendata']))) / float(len(data['lendata']))
                for i in range(len(data['lendata'])):
                    data['lendata'][i] -= lm

                List = cdata.append
                for i in range(len(enurows)):
                    current_res = {'date': j2k_to_date(data['t'][i], tz).strftime('%Y-%m-%d %H:%M:%S.%f'), 'rank': data['r'][i]}
                    if 'east' in args['series']:
                        current_res['east'] = enurows[i, 0]
                    if 'north' in args['series']:
                        current_res['north'] = enurows[i,1]
                    if 'up' in args['series']:
                        current_res['up'] = enurows[i,2]
                    if 'length' in args['series']:
                        current_res['length'] = data['lendata'][i]
                    List(current_res)

                q_data[channel] = cdata
                count += len(cdata)

        return { 'nr': count, 'records': q_data }, 200

    @staticmethod
    def get_gps_data(channel, args, dates):
        """Given a channel and input args, query the database for the gps data and then perform the various
        calculations on it prior to sending it back to the user.

        Parameters:
        channel -- the channel to be queried
        args    -- the args dictionary passed into this request
        dates   -- three-item list containing start and end timestamps and timezone info

        Returns:
        An array of dictionaries containing all computed GPS data
        """
        queryclauses = []
        orderby      = []

        id = GPSChannel.query.filter(GPSChannel.code == channel.upper()).one().cid

        tz = dates[2]
        queryclauses.append(GPSChannel.cid == id)
        queryclauses.append(GPSSource.avgdate.between(date_to_j2k(dates[0], tz), date_to_j2k(dates[1], tz)))

        if args['rank'] != 0:
            queryclauses.append(GPSRank.rid == args['rank'])

        orderby.append(GPSSource.avgdate.asc())
        orderby.append(GPSRank.rank.desc())

        if args['downsample'] == 'none':
            q = Solution.query.join(GPSSource).join(GPSChannel).join(GPSRank)\
                .filter(*queryclauses).order_by(*orderby)

            try:
                q = q.limit(MAX_LINES['GPS'])
            except KeyError:
                pass
            data = q.all()
        elif args['downsample'] == 'decimate':
            interval = args['dsint']
            dbname   = 'v3_hvo_deformation_gps$gps'
            s        = "SELECT * FROM(SELECT fullquery.*, @row := @row+1 as rownum FROM (SELECT "\
                        "(j2ksec0 + j2ksec1) / 2 as t, d.rid as r, x, y, z, sxx, syy, szz, sxy, sxz, syz FROM "\
                        + dbname + ".solutions a INNER JOIN " + dbname + ".channels b on a.cid = b.cid INNER JOIN "\
                        + dbname + ".sources c on a.sid = c.sid INNER JOIN " + dbname + ".ranks d on c.rid = d.rid "\
                        "WHERE b.cid = :cid AND (c.j2ksec0 + c.j2ksec1) / 2 BETWEEN :st AND :et "
            if args['rank'] != 0:
                s += "AND d.rid = :rid ORDER BY 1 ASC"
            else:
                s += "ORDER BY 1 ASC, d.rid DESC"
            s += ") fullquery, (SELECT @row:=0) r) ranked WHERE rownum % :dsint = 1"
            try:
                s += ' limit ' + str(MAX_LINES['GPS'])
            except KeyError:
                pass
            data = db.session.execute(text(s), params=dict(dsint=interval, st=date_to_j2k(dates[0], tz),
                                        et=date_to_j2k(dates[1], tz), rid=args['rank'], cid=id)).fetchall()
        elif args['downsample'] == 'mean':
            q_items = []
            interval = args['dsint']
            q_items.extend([func.min(GPSSource.avgdate).label('t'), func.min(GPSRank.rid).label('r')])
            q_items.extend([func.avg(Solution.x).label('x'), func.avg(Solution.y).label('y'),
                            func.avg(Solution.z).label('z'), func.avg(Solution.sxx).label('sxx'),
                            func.avg(Solution.syy).label('syy'), func.avg(Solution.szz).label('szz'),
                            func.avg(Solution.sxy).label('sxy'), func.avg(Solution.sxz).label('sxz'),
                            func.avg(Solution.syz).label('syz')])
            q_items.append(((GPSSource.avgdate)-date_to_j2k(dates[0], tz)).self_group().op('div')(interval).label('intNum'))
            q = db.session.query(*q_items).select_from(Solution).join(GPSChannel, GPSSource, GPSRank)
            q = q.filter(*queryclauses).order_by(*orderby).group_by('intNum')
            try:
                q = q.limit(MAX_LINES['GPS'])
            except KeyError:
                pass
            data = q.all()

        # Loop through and remove data with duplicate time stamps.
        # Note: I think we should only have to do this in the case of 'best rank'
        if args['rank'] == 0:
            res = []
            tmpj2k = 0
            for d in data:
                if not tmpj2k == d.timestamp:
                    res.append(d)
                    tmpj2k = d.timestamp
            return GPSAPI.set_to_list(res)
        else:
            return GPSAPI.set_to_list(data)

    @staticmethod
    def apply_baseline(baseline, d):
        """Subtracts position and adds covariance of specified baseline data at subset of times
        common to both baseline data and data being altered.

        Parameters:
        baseline    -- GPS data from the baseline channel given start and end times
        d           -- GPS data from the channel being looked at

        Returns:
        Altered 'd' data structure
        """
        si      = 0
        bi      = 0
        newdata = []
        while True:
            st = d['t'][si]
            bt = baseline['t'][bi]
            if fabs(st - bt) < 0.001:
                t    = st
                r    = d['r'][si]
                x    = d['xyz'][si*3] - baseline['xyz'][bi*3]
                y    = d['xyz'][si*3+1] - baseline['xyz'][bi*3+1]
                z    = d['xyz'][si*3+2] - baseline['xyz'][bi*3+2]
                sxx  = d['cov'][si*3, si*3] + baseline['cov'][bi*3, bi*3]
                syy  = d['cov'][si*3+1, si*3+1] + baseline['cov'][bi*3+1, bi*3+1]
                szz  = d['cov'][si*3+2, si*3+2] + baseline['cov'][bi*3+2, bi*3+2]
                sxy  = d['cov'][si*3, si*3+1] + baseline['cov'][bi*3, bi*3+1]
                sxz  = d['cov'][si*3, si*3+2] + baseline['cov'][bi*3, bi*3+2]
                syz  = d['cov'][si*3+1, si*3+2] + baseline['cov'][bi*3+1, bi*3+2]
                nlen = sqrt(x*x + y*y + z*z)
                newdata.append(GPSDataPoint(t, r, x, y, z, sxx, syy, szz, sxy, sxz, syz, nlen))
                si += 1
                bi += 1
            else:
                if st < bt:
                    si += 1
                    while si < len(d['t']) and d['t'][si] < baseline['t'][bi]:
                        si += 1
                    if si == len(d['t']):
                        break
                else:
                    bi += 1
                    while bi < len(baseline['t']) and baseline['t'][bi] < d['t'][si]:
                        bi += 1
                    if bi == len(baseline['t']):
                        break
            if si == len(d['t']) or bi == len(baseline['t']):
                break
        return GPSAPI.set_to_list(newdata)

    @staticmethod
    def set_to_list(d):
        """Given raw data, create data structures for use in later calculations"""
        if len(d) == 0:
            return {}
        else:
            r       = []
            t       = []
            xyz     = []
            lendata = []
            cov     = matrix(zeros((len(d)*3, len(d)*3)))
            origin  = d[0]
            for idx,val in enumerate(d):
                try:
                    t.append(val.source.avgdate)
                    r.append(val.source.rank.name)
                except AttributeError:
                    t.append(val.t)
                    r.append(val.r)
                xyz.extend([val.x, val.y, val.z])
                cov[idx*3, idx*3]     = val.sxx
                cov[idx*3, idx*3+1]   = val.sxy
                cov[idx*3, idx*3+2]   = val.sxz
                cov[idx*3+1, idx*3]   = val.sxy
                cov[idx*3+1, idx*3+1] = val.syy
                cov[idx*3+1, idx*3+2] = val.syz
                cov[idx*3+2, idx*3]   = val.sxz
                cov[idx*3+2, idx*3+1] = val.syz
                cov[idx*3+2, idx*3+2] = val.szz
                try:
                    lendata.append(val.nlen)
                except AttributeError:
                    dx = val.x - origin.x
                    dy = val.y - origin.y
                    dz = val.z - origin.z
                    lendata.append(sqrt(dx*dx + dy*dy + dz*dz))
            return { 'r': r, 't': t, 'xyz': xyz, 'lendata': lendata, 'cov': cov }

    @staticmethod
    def column_3N_to_rows(rm):
        """Rearranges columnar 3*Nx1 matrix to an Nx3 row matrix"""
        r = matrix(zeros((len(rm)/3, 3)))
        for i in range(len(rm)/3):
            r[i, 0] = rm[i*3, 0]
            r[i, 1] = rm[i*3 + 1, 0]
            r[i, 2] = rm[i*3 + 2, 0]
        return r


    @staticmethod
    def xyz_to_llh(x, y, z):
        """Converty XYZ coordinate into longitude/latitude/height coordinates"""
        llh = []
        da  = 0.0
        df  = 0.0
        a   = 6378137 - da
        f   = 1 / 298.2572235630 - df
        b   = (1 - f) * a
        e2  = 2 * f - f * f
        E2  = (a * a - b * b) / (b * b)
        p   = sqrt(x * x + y * y)

        llh.append(atan2(y, x))
        theta = atan((z * a) / (p * b))
        llh.append(atan((z + E2 * b * fpow(sin(theta), 3)) / (p - e2 * a * fpow(cos(theta), 3))))
        N = a / sqrt(1 - e2 * sin(llh[1]) * sin(llh[1]))
        llh.append(p / cos(llh[1]) - N)
        llh[0] = degrees(llh[0])
        llh[1] = degrees(llh[1])

        return llh

    @staticmethod
    def to_enu(lon, lat, size, xyz, cov):
        """Converts xyz position data to east/north/up (ENU) position data"""
        t      = GPSAPI.createENUTransform(lon, lat)
        tt     = t.T
        tmpxyz = []
        tmpcov = matrix(zeros((size * 3,size * 3)))

        for i in range(size):
            tmp = matrix([[xyz[i*3]], [xyz[i * 3 + 1]], [xyz[i * 3 + 2]]])
            tmpxyz.append(t * matrix([[xyz[i*3]], [xyz[i * 3 + 1]], [xyz[i * 3 + 2]]]))
            copyto(tmpcov[i*3:i*3+3, i*3:i*3+3], (t * cov[i*3:i*3+3, i*3:i*3+3]) * tt)

        return concatenate(tmpxyz), tmpcov

    @staticmethod
    def createENUTransform(lon, lat):
        """Creates a transformation matrix for tranlating from lon/lat/height to east/north/up"""
        sinlon = sin(radians(lon))
        sinlat = sin(radians(lat))
        coslon = cos(radians(lon))
        coslat = cos(radians(lat))
        return matrix([[-sinlon, coslon, 0],
                       [-sinlat * coslon, -sinlat * sinlon, coslat],
                       [coslat * coslon, coslat * sinlon, sinlat]])

    @staticmethod
    def create_param_string():
        if not current_app.debug:
            settings = current_app.config.get('RESTFUL_JSON', {})
            settings.setdefault('indent', 4)
            settings.setdefault('sort_keys', True)
            current_app.config['RESTFUL_JSON'] = settings

        gps_channels    = [x.code for x in GPSChannel.query.all()]
        params            = {}
        params['channel'] = {'type': 'string', 'required': 'yes', 'note': 'Can be comma-separated list.',
                            'options': gps_channels}
        params['baseline'] = {'type': 'string', 'required': 'no', 'note': 'Can be comma-separated list.',
                            'options': gps_channels}
        params['starttime'] = {'type': 'string', 'required': 'yes',
                              'note': 'Will also accept things like -6m for last six months.',
                              'format': 'yyyy[MMdd[hhmm]]'}
        params['endtime'] = {'type': 'string', 'required': 'no', 'format': 'yyyy[MMdd[hhmm]]', 'default': 'now'}
        params['rank'] = {'type': 'int', 'required': 'no', 'default': 8,
                         'note': 'A rank of 0 will return the best possible rank.'}
        params['timezone'] = {'type': 'string', 'required': 'no', 'default': 'hst'}
        params['series'] = {'type': 'string', 'required': 'no', 'note': 'Can be comma-separated list.',
                            'default': 'east,north,up', 'options': _series_options}
        params['downsample'] = {'type': 'string', 'required': 'no', 'default': 'none', 'options': DS_OPTIONS}
        params['dsint'] = {'type': 'int', 'required': 'no'}
        return params
