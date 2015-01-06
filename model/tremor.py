from sqlalchemy.ext.declarative import declared_attr
from valverest.database import db

class catalog(db.Model):
    __tablename__ = 'tremor_catalog'
    __bind_key__  = 'tremor'

    evid      = db.Column(db.Integer, primary_key=True)
    methodid  = db.Column(db.Integer)
    starttime = db.Column(db.DateTime)
    latitude  = db.Column(db.Float)
    longitude = db.Column(db.Float)
    depth     = db.Column(db.Float)
    region    = db.Column(db.String(2))
    iseq      = db.Column(db.Integer)

    def __repr__(self):
    	return '%s, %f, %f, %f, region=%s, iseq=%d' % (self.starttime,self.latitude,self.longitude,self.depth, self.region, self.iseq)
