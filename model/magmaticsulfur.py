from valverest.database import db4 as db
from valverest.util import date_to_j2k

class MagmaticSulfurBase(object):
    __bind_key__ = 'magmaticsulfur'

    timestamp   = db.Column('j2ksec', db.Float, primary_key=True)
    olvinc_sppm = db.Column(db.Float)
    sid         = db.Column('id', db.Float)
    tid         = db.Column(db.Integer)
    rid         = db.Column(db.Integer, primary_key=True)

class KERZ(MagmaticSulfurBase, db.Model):
    __tablename__ = 'KERZ'
    __bind_key__  = 'magmaticsulfur'

    def __init__(self, time='', olvinc_sppm='', sid=''):
        self.timestamp   = date_to_j2k(time, False)
        self.olvinc_sppm = '%.2f' % float(olvinc_sppm) if olvinc_sppm != '' else None
        self.sid         = sid if sid != '' else None
        self.tid         = 3
        self.rid         = 1

class HMM(MagmaticSulfurBase, db.Model):
    __tablename__ = 'HMM'
    __bind_key__  = 'magmaticsulfur'

    def __init__(self, time='', olvinc_sppm='', sid=''):
        self.timestamp   = date_to_j2k(time, False)
        self.olvinc_sppm = '%.2f' % float(olvinc_sppm) if olvinc_sppm != '' else None
        self.sid         = sid if sid != '' else None
        self.tid         = 2
        self.rid         = 1
