# -*- coding: utf-8 -*-
from valverest.database import db4 as db


class Hypocenter(db.Model):
    __tablename__ = 'hypocenters'
    __bind_key__ = 'hypocenter'

    timestamp = db.Column('j2ksec', db.Float)
    eid = db.Column(db.String(45), primary_key=True)
    rid = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    depth = db.Column(db.Float)
    prefmag = db.Column(db.Float)
    ampmag = db.Column(db.Float)
    codamag = db.Column(db.Float)
    nphases = db.Column(db.Integer)
    azgap = db.Column(db.Integer)
    dmin = db.Column(db.Float)
    rms = db.Column(db.Float)
    nstimes = db.Column(db.Integer)
    herr = db.Column(db.Float)
    verr = db.Column(db.Float)
    magtype = db.Column(db.String(1))
    rmk = db.Column(db.String(1))

    # Relationships
    rank = db.relationship('HypocenterRank', uselist=False, viewonly=True)
    remark = db.relationship('HypocenterRemark', uselist=False, viewonly=True)


class HypocenterRank(db.Model):
    __tablename__ = 'ranks'
    __bind_key__ = 'hypocenter'

    rid = db.Column(db.Integer, db.ForeignKey('hypocenters.rid'),
                    primary_key=True)
    name = db.Column(db.String(24))
    rank = db.Column(db.Integer)


class HypocenterRemark(db.Model):
    __tablename__ = 'options_remark'
    __bind_key__ = 'hypocenter'

    id = db.Column(db.Integer, primary_key=True)
    idx = db.Column(db.Integer)
    code = db.Column(db.String, db.ForeignKey('hypocenters.rmk'))
    name = db.Column(db.String)
