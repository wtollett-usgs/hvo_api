from sqlalchemy.ext.declarative import declared_attr
from valverest.database import db3 as db
from valverest.util import date_to_j2k

class IncompatiblesBase(object):
    __bind_key__ = 'incompatibles'
    
    timestamp     = db.Column('j2ksec', db.Float, primary_key=True)
    wr_k2o_tio2   = db.Column(db.Float)
    gls_k2o_tio2  = db.Column(db.Float)
    wr_cao_al2o3  = db.Column(db.Float)
    wr_cao_tio2   = db.Column(db.Float)
    wr_la_yb_inaa = db.Column(db.Float)
    wr_zr_y_wdx   = db.Column(db.Float)
    wr_zr_y_edx   = db.Column(db.Float)
    wr_sr_edx     = db.Column(db.Float)
    sid           = db.Column('id', db.Float)
    tid           = db.Column(db.Integer)
    rid           = db.Column(db.Integer, primary_key=True)

class KERZ(IncompatiblesBase, db.Model):
    __tablename__ = 'KERZ'
    __bind_key__  = 'incompatibles'
    
    def __init__(self, time='', wr_k2o_tio2='', gls_k2o_tio2='', wr_cao_al2o3='', wr_cao_tio2='', wr_la_yb_inaa='', 
                 wr_zr_y_wdx='', wr_zr_y_edx='', wr_sr_edx='', sid=''):
        self.timestamp     = date_to_j2k(time, False)
        self.wr_k2o_tio2   = '%.3f' % float(wr_k2o_tio2) if wr_k2o_tio2 != '' else None
        self.gls_k2o_tio2  = '%.3f' % float(gls_k2o_tio2) if gls_k2o_tio2 != '' else None
        self.wr_cao_al2o3  = '%.3f' % float(wr_cao_al2o3) if wr_cao_al2o3 != '' else None
        self.wr_cao_tio2   = '%.3f' % float(wr_cao_tio2) if wr_cao_tio2 != '' else None
        self.wr_la_yb_inaa = '%.3f' % float(wr_la_yb_inaa) if wr_la_yb_inaa != '' else None
        self.wr_zr_y_wdx   = '%.3f' % float(wr_zr_y_wdx) if wr_zr_y_wdx != '' else None
        self.wr_zr_y_edx   = '%.3f' % float(wr_zr_y_edx) if wr_zr_y_edx != '' else None
        self.wr_sr_edx     = '%.3f' % float(wr_sr_edx) if wr_sr_edx != '' else None
        self.sid           = sid if sid != '' else None
        self.tid           = 3
        self.rid           = 1
    
class HMM(IncompatiblesBase, db.Model):
    __tablename__ = 'HMM'
    __bind_key__  = 'incompatibles'
    
    def __init__(self, time='', wr_k2o_tio2='', gls_k2o_tio2='', wr_cao_al2o3='', wr_cao_tio2='', wr_la_yb_inaa='', 
                 wr_zr_y_wdx='', wr_zr_y_edx='', wr_sr_edx='', sid=''):
        self.timestamp     = date_to_j2k(time, False)
        self.wr_k2o_tio2   = '%.3f' % float(wr_k2o_tio2) if wr_k2o_tio2 != '' else None
        self.gls_k2o_tio2  = '%.3f' % float(gls_k2o_tio2) if gls_k2o_tio2 != '' else None
        self.wr_cao_al2o3  = '%.3f' % float(wr_cao_al2o3) if wr_cao_al2o3 != '' else None
        self.wr_cao_tio2   = '%.3f' % float(wr_cao_tio2) if wr_cao_tio2 != '' else None
        self.wr_la_yb_inaa = '%.3f' % float(wr_la_yb_inaa) if wr_la_yb_inaa != '' else None
        self.wr_zr_y_wdx   = '%.3f' % float(wr_zr_y_wdx) if wr_zr_y_wdx != '' else None
        self.wr_zr_y_edx   = '%.3f' % float(wr_zr_y_edx) if wr_zr_y_edx != '' else None
        self.wr_sr_edx     = '%.3f' % float(wr_sr_edx) if wr_sr_edx != '' else None
        self.sid           = sid if sid != '' else None
        self.tid           = 2
        self.rid           = 1
