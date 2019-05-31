# -*- coding: utf-8 -*-
from valverest.database import db13 as db
from sqlalchemy.ext.declarative import declared_attr

_tablenames = ['UWEV', 'HOVL', 'PUOC', 'NPIT', 'CALM']
_ridkeys = [db.ForeignKey(x + '.rid') for x in _tablenames]


class GravityBase(object):
    __bind_key__ = 'gravity'

    timestamp = db.Column('j2ksec', db.Float, primary_key=True)
    gravity = db.Column(db.Float)
    crosslevel = db.Column(db.Float)
    longlevel = db.Column(db.Float)
    airpressure = db.Column(db.Float)
    insttemp = db.Column(db.Float)
    instvolt = db.Column(db.Float)
    tid = db.Column(db.Integer)
    rid = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def rank(self):
        return db.relationship('GravityRank', uselist=False,
                               viewonly=True)


class GravityRank(db.Model):
    __tablename__ = 'ranks'
    __bind_key__ = 'gravity'

    rid = db.Column(db.Integer, *_ridkeys, primary_key=True)
    name = db.Column(db.String(24), unique=True)
    rank = db.Column(db.Integer)


for name in _tablenames:
    c = type(name.upper(),
             (GravityBase, db.Model),
             {'__bind_key__': 'gravity', '__tablename__': name})
    globals()[c.__name__] = c
    del c
