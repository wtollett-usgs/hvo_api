# -*- coding: utf-8 -*-
from valverest.database import db
from valverest.util import date_to_j2k


class HMM(db.Model):
    __tablename__ = 'HMM'
    __bind_key__ = 'ash'

    timestamp = db.Column('j2ksec', db.Float, primary_key=True)
    accumrate = db.Column(db.Float)
    percentjuvenile = db.Column(db.Float)
    tid = db.Column(db.Integer)
    rid = db.Column(db.Integer, primary_key=True)

    def __init__(self, time='', ar='', pj=''):
        self.timestamp = date_to_j2k(time, False)
        self.accumrate = '%.3f' % float(ar) if ar != '' else None
        self.percentjuvenile = '%.2f' % float(pj) if pj != '' else None
        self.tid = 2
        self.rid = 1
