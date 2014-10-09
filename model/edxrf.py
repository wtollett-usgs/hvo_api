from sqlalchemy.ext.declarative import declared_attr
from valverest.database import db
from valverest.util import date_to_j2k

class EDXRFBase(object):
    __bind_key__ = 'edxrf'

    timestamp = db.Column('j2ksec', db.Float, primary_key=True)
    rb        = db.Column(db.Float)
    sr        = db.Column(db.Float)
    y         = db.Column(db.Float)
    zr        = db.Column(db.Float)
    nb        = db.Column(db.Float)
    tid       = db.Column(db.Integer)
    rid       = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def rank(self):
        return db.relationship('EDXRFRank', uselist=False)

    @declared_attr
    def translation(self):
        return db.relationship('EDXRFTranslation', uselist=False)

class KIERZ(EDXRFBase, db.Model):
    __tablename__ = 'KIERZ'
    __bind_key__  = 'edxrf'

    def __init__(self, time='', rb='', sr='', y='', zr='', nb=''):
        self.timestamp = date_to_j2k(time, False)
        self.rb        = '%.2f' % float(rb) if rb != '' else None
        self.sr        = '%.2f' % float(sr) if sr != '' else None
        self.y         = '%.2f' % float(y) if y != '' else None
        self.zr        = '%.2f' % float(zr) if zr != '' else None
        self.nb        = '%.2f' % float(nb) if nb != '' else None
        self.tid       = 3
        self.rid       = 1

class KISUM(EDXRFBase, db.Model):
    __tablename__ = 'KISUM'
    __bind_key__  = 'edxrf'

    def __init__(self, time='', rb='', sr='', y='', zr='', nb=''):
        self.timestamp = date_to_j2k(time, False)
        self.rb        = '%.2f' % float(rb) if rb != '' else None
        self.sr        = '%.2f' % float(sr) if sr != '' else None
        self.y         = '%.2f' % float(y) if y != '' else None
        self.zr        = '%.2f' % float(zr) if zr != '' else None
        self.nb        = '%.2f' % float(nb) if nb != '' else None
        self.tid       = 2
        self.rid       = 1

class EDXRFRank(db.Model):
    __tablename__ = 'ranks'
    __bind_key__  = 'edxrf'

    rid  = db.Column(db.Integer, db.ForeignKey('KIERZ.rid'), db.ForeignKey('KISUM.rid'), primary_key=True)
    name = db.Column(db.String(24), unique=True)
    rank = db.Column(db.Integer)

class EDXRFTranslation(db.Model):
    __tablename__ = 'translations'
    __bind_key__  = 'edxrf'

    tid  = db.Column(db.Integer, db.ForeignKey('KIERZ.tid'), db.ForeignKey('KISUM.tid'), primary_key=True)
    name = db.Column(db.String(255))
    crb  = db.Column(db.Float)
    drb  = db.Column(db.Float)
    csr  = db.Column(db.Float)
    dsr  = db.Column(db.Float)
    cy   = db.Column(db.Float)
    dy   = db.Column(db.Float)
    czr  = db.Column(db.Float)
    dzr  = db.Column(db.Float)
    cnb  = db.Column(db.Float)
    dnb  = db.Column(db.Float)
