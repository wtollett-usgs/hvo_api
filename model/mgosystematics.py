from sqlalchemy.ext.declarative import declared_attr
from valverest.database import db2 as db
from valverest.util import date_to_j2k

class MgOSystematicsBase(object):
    __bind_key__ = 'mgosys'
    
    timestamp        = db.Column('j2ksec', db.Float, primary_key=True)
    wr_mgo_wt        = db.Column(db.Float)
    gls_mgo_wt       = db.Column(db.Float)
    gls_mgo_tempcorr = db.Column(db.Float)
    wr_mgo_temp      = db.Column(db.Float)
    wr_fo_clc        = db.Column(db.Float)
    gls_fo_clccorr   = db.Column(db.Float)
    olv_fo_meas      = db.Column(db.Float)
    sid              = db.Column('id', db.Float)
    tid              = db.Column(db.Integer)
    rid              = db.Column(db.Integer, primary_key=True)

class KERZ(MgOSystematicsBase, db.Model):
    __tablename__ = 'KERZ'
    __bind_key__  = 'mgosys'
    
    def __init__(self, time='', wr_mgo_wt='', gls_mgo_wt='', gls_mgo_tempcorr='', wr_mgo_temp='', wr_fo_clc='', 
                 gls_fo_clccorr='', olv_fo_meas='', sid=''):
        self.timestamp        = date_to_j2k(time, False)
        self.wr_mgo_wt        = '%.2f' % float(wr_mgo_wt) if wr_mgo_wt != '' else None
        self.gls_mgo_wt       = '%.2f' % float(gls_mgo_wt) if gls_mgo_wt != '' else None
        self.gls_mgo_tempcorr = '%.2f' % float(gls_mgo_tempcorr) if gls_mgo_tempcorr != '' else None
        self.wr_mgo_temp      = '%.2f' % float(wr_mgo_temp) if wr_mgo_temp != '' else None
        self.wr_fo_clc        = '%.2f' % float(wr_fo_clc) if wr_fo_clc != '' else None
        self.gls_fo_clccorr   = '%.2f' % float(gls_fo_clccorr) if gls_fo_clccorr != '' else None
        self.olv_fo_meas      = '%.2f' % float(olv_fo_meas) if olv_fo_meas != '' else None
        self.sid              = sid if sid != '' else None
        self.tid              = 3
        self.rid              = 1
    
class HMM(MgOSystematicsBase, db.Model):
    __tablename__ = 'HMM'
    __bind_key__  = 'mgosys'
    
    def __init__(self, time='', wr_mgo_wt='', gls_mgo_wt='', gls_mgo_tempcorr='', wr_mgo_temp='', wr_fo_clc='', 
                 gls_fo_clccorr='', olv_fo_meas='', sid=''):
        self.timestamp        = date_to_j2k(time, False)
        self.wr_mgo_wt        = '%.2f' % float(wr_mgo_wt) if wr_mgo_wt != '' else None
        self.gls_mgo_wt       = '%.2f' % float(gls_mgo_wt) if gls_mgo_wt != '' else None
        self.gls_mgo_tempcorr = '%.2f' % float(gls_mgo_tempcorr) if gls_mgo_tempcorr != '' else None
        self.wr_mgo_temp      = '%.2f' % float(wr_mgo_temp) if wr_mgo_temp != '' else None
        self.wr_fo_clc        = '%.2f' % float(wr_fo_clc) if wr_fo_clc != '' else None
        self.gls_fo_clccorr   = '%.2f' % float(gls_fo_clccorr) if gls_fo_clccorr != '' else None
        self.olv_fo_meas      = '%.2f' % float(olv_fo_meas) if olv_fo_meas != '' else None
        self.sid              = sid if sid != '' else None
        self.tid              = 2
        self.rid              = 1