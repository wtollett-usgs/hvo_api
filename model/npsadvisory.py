# -*- coding: utf-8 -*-
from valverest.database import db12 as db
from sqlalchemy.ext.declarative import declared_attr

_tablenames = ['HAVO_CHA', 'HAVO_CMP', 'HAVO_DEV', 'HAVO_KVC', 'HAVO_NAU',
               'HAVO_OBS', 'HAVO_PRK', 'HAVO_STE', 'HAVO_THU']
_ridkeys = [db.ForeignKey(x + '.rid') for x in _tablenames]
_tidkeys = [db.ForeignKey(x + '.tid') for x in _tablenames]


class NPSAdvisoryBase(object):
    __bind_key__ = 'npsadvisory'

    timestamp = db.Column('j2ksec', db.Float, primary_key=True)
    avgso2 = db.Column(db.Float)
    pm25 = db.Column(db.Float)
    windspeed = db.Column(db.Float)
    winddir = db.Column(db.Float)
    winddirsd = db.Column(db.Float)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    insttemp = db.Column(db.Float)
    instvolt = db.Column(db.Float)
    cal = db.Column(db.Float)
    tid = db.Column(db.Integer)
    rid = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def rank(self):
        return db.relationship('NPSAdvisoryRank', uselist=False, viewonly=True)

    @declared_attr
    def translation(self):
        return db.relationship('NPSAdvisoryTranslation', uselist=False,
                               viewonly=True)


class NPSAdvisoryRank(db.Model):
    __tablename__ = 'ranks'
    __bind_key__ = 'npsadvisory'

    rid = db.Column(db.Integer, *_ridkeys, primary_key=True)
    name = db.Column(db.String(24), unique=True)
    rank = db.Column(db.Integer)


class NPSAdvisoryTranslation(db.Model):
    __tablename__ = 'translations'
    __bind_key__ = 'npsadvisory'

    tid = db.Column(db.Integer, *_tidkeys, primary_key=True)
    name = db.Column(db.String(255))
    cavgso2 = db.Column(db.Float)
    davgso2 = db.Column(db.Float)
    cpm25 = db.Column(db.Float)
    dpm25 = db.Column(db.Float)
    cwindspeed = db.Column(db.Float)
    dwindspeed = db.Column(db.Float)
    cwinddir = db.Column(db.Float)
    dwinddir = db.Column(db.Float)
    cwinddirsd = db.Column(db.Float)
    dwinddirsd = db.Column(db.Float)
    ctemperature = db.Column(db.Float)
    dtemperature = db.Column(db.Float)
    chumidity = db.Column(db.Float)
    dhumidity = db.Column(db.Float)
    cpressure = db.Column(db.Float)
    dpressure = db.Column(db.Float)
    crainfall = db.Column(db.Float)
    drainfall = db.Column(db.Float)
    cinsttemp = db.Column(db.Float)
    dinsttemp = db.Column(db.Float)
    cinstvolt = db.Column(db.Float)
    dinstvolt = db.Column(db.Float)
    ccal = db.Column(db.Float)
    dcal = db.Column(db.Float)


for name in _tablenames:
    c = type(name.upper(),
             (NPSAdvisoryBase, db.Model),
             {'__bind_key__': 'npsadvisory', '__tablename__': name})
    globals()[c.__name__] = c
    del c
