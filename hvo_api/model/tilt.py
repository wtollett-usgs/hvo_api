# -*- coding: utf-8 -*-
from valverest.database import db2 as db
from sqlalchemy.ext.declarative import declared_attr

_tablenames = ['BLB', 'ESC', 'HEI', 'HOK', 'IKI', 'JKA', 'KAE', 'KNP', 'KWL',
               'MCC', 'MKI', 'MLO', 'MLS', 'MOK', 'MUL', 'POC', 'POO', 'POS',
               'SDH', 'SLC', 'SMC', 'TST', 'UWD', 'UWE', 'UWT', 'WBO']
_tidkeys = [db.ForeignKey(x + '.tid') for x in _tablenames]
_ridkeys = [db.ForeignKey(x + '.rid') for x in _tablenames]


class TiltBase(object):
    __bind_key__ = 'tilt'

    timestamp = db.Column('j2ksec', db.Float, primary_key=True)
    xTilt = db.Column(db.Float)
    yTilt = db.Column(db.Float)
    holeTemp = db.Column(db.Float)
    boxTemp = db.Column(db.Float)
    instVolt = db.Column(db.Float)
    gndVolt = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    tid = db.Column(db.Integer)
    rid = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def rank(self):
        return db.relationship('TiltRank', uselist=False, viewonly=True)

    @declared_attr
    def translation(self):
        return db.relationship('TiltTranslation', uselist=False, viewonly=True)


class TiltTranslation(db.Model):
    __tablename__ = 'translations'
    __bind_key__ = 'tilt'

    tid = db.Column(db.Integer, *_tidkeys, primary_key=True)
    name = db.Column(db.String(255))
    cxTilt = db.Column(db.Float)
    dxTilt = db.Column(db.Float)
    cyTilt = db.Column(db.Float)
    dyTilt = db.Column(db.Float)
    choleTemp = db.Column(db.Float)
    dholeTemp = db.Column(db.Float)
    cboxTemp = db.Column(db.Float)
    dboxTemp = db.Column(db.Float)
    cinstVolt = db.Column(db.Float)
    dinstVolt = db.Column(db.Float)
    cgndVolt = db.Column(db.Float)
    dgndVolt = db.Column(db.Float)
    crainfall = db.Column(db.Float)
    drainfall = db.Column(db.Float)
    azimuth = db.Column(db.Float)


class TiltChannel(db.Model):
    __tablename__ = 'channels'
    __bind_key__ = 'tilt'

    cid = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), unique=True)
    name = db.Column(db.String(255))
    lon = db.Column(db.Float)
    lat = db.Column(db.Float)
    height = db.Column(db.Float)
    azimuth = db.Column(db.Float)
    tid = db.Column(db.Integer)


class TiltRank(db.Model):
    __tablename__ = 'ranks'
    __bind_key__ = 'tilt'

    rid = db.Column(db.Integer, *_ridkeys, primary_key=True)
    name = db.Column(db.String(24), unique=True)
    rank = db.Column(db.Integer)


for name in _tablenames:
    c = type(name.upper(), (TiltBase, db.Model),
             {'__bind_key__': 'tilt', '__tablename__': name})
    globals()[c.__name__] = c
    del c
