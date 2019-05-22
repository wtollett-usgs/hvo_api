# -*- coding: utf-8 -*-
from valverest.database import db11 as db
from sqlalchemy.ext.declarative import declared_attr

_tablenames = ['COC', 'LERZ', 'SUM', 'SUMDFW']
_ridkeys = [db.ForeignKey(x + '.rid') for x in _tablenames]
_tidkeys = [db.ForeignKey(x + '.tid') for x in _tablenames]


class SO2EmissionsBase(object):
    __bind_key__ = 'so2emissions'

    timestamp = db.Column('j2ksec', db.Float, primary_key=True)
    so2 = db.Column(db.Float)
    so2sd = db.Column(db.Float)
    windspeed = db.Column(db.Float)
    winddir = db.Column(db.Float)
    samples = db.Column(db.Float)
    sampleNumber = db.Column(db.Float)
    tid = db.Column(db.Integer)
    rid = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def rank(self):
        return db.relationship('SO2EmissionsRank', uselist=False,
                               viewonly=True)


class SO2EmissionsRank(db.Model):
    __tablename__ = 'ranks'
    __bind_key__ = 'so2emissions'

    rid = db.Column(db.Integer, *_ridkeys, primary_key=True)
    name = db.Column(db.String(24), unique=True)
    rank = db.Column(db.Integer)


for name in _tablenames:
    c = type(name.upper(),
             (SO2EmissionsBase, db.Model),
             {'__bind_key__': 'so2emissions', '__tablename__': name})
    globals()[c.__name__] = c
    del c
