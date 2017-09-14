from valverest.database import db7 as db
from sqlalchemy.ext.hybrid import hybrid_property

class Solution(db.Model):
    __tablename__ = 'solutions'
    __bind_key__  = 'gps'

    sid = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.Integer, primary_key=True)
    x   = db.Column(db.Float)
    y   = db.Column(db.Float)
    z   = db.Column(db.Float)
    sxx = db.Column(db.Float)
    syy = db.Column(db.Float)
    szz = db.Column(db.Float)
    sxy = db.Column(db.Float)
    sxz = db.Column(db.Float)
    syz = db.Column(db.Float)

    # Relationships
    source  = db.relationship('GPSSource', uselist=False)
    channel = db.relationship('GPSChannel', uselist=False)

class GPSSource(db.Model):
    __tablename__ = 'sources'
    __bind_key__  = 'gps'

    sid   = db.Column(db.Integer, db.ForeignKey('solutions.sid'), primary_key=True)
    name  = db.Column(db.String(255))
    hash  = db.Column(db.String(32))
    date0 = db.Column('j2ksec0', db.Float, primary_key=True)
    date1 = db.Column('j2ksec1', db.Float, primary_key=True)
    rid   = db.Column(db.Integer)

    # Relationships
    rank = db.relationship('GPSRank', uselist=False)

    @hybrid_property
    def avgdate(self):
        return (self.date0 + self.date1) / 2

class GPSChannel(db.Model):
    __tablename__ = 'channels'
    __bind_key__  = 'gps'

    cid    = db.Column(db.Integer, db.ForeignKey('solutions.cid'), primary_key=True)
    code   = db.Column(db.String(16))
    name   = db.Column(db.String(255))
    lon    = db.Column(db.Float)
    lat    = db.Column(db.Float)
    height = db.Column(db.Float)
    ctid   = db.Column(db.Integer)

class GPSRank(db.Model):
    __tablename__ = 'ranks'
    __bind_key__  = 'gps'

    rid  = db.Column(db.Integer, db.ForeignKey('sources.rid'), primary_key=True)
    name = db.Column(db.String(24))
    rank = db.Column(db.Integer)

class GPSDataPoint(object):
    def __init__(self, t, r, x, y, z, sxx, syy, szz, sxy, sxz, syz, nlen):
        self._t    = t
        self._r    = r
        self._x    = x
        self._y    = y
        self._z    = z
        self._sxx  = sxx
        self._syy  = syy
        self._szz  = szz
        self._sxy  = sxy
        self._sxz  = sxz
        self._syz  = syz
        self._nlen = nlen

    @property
    def t(self):
        return self._t

    @property
    def r(self):
        return self._r

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    @property
    def sxx(self):
        return self._sxx

    @property
    def syy(self):
        return self._syy

    @property
    def szz(self):
        return self._szz

    @property
    def sxy(self):
        return self._sxy

    @property
    def sxz(self):
        return self._sxz

    @property
    def syz(self):
        return self._syz

    @property
    def nlen(self):
        return self._nlen
