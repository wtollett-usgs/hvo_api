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
    stations  = db.relationship('station', backref='catalog')

    def __repr__(self):
    	return '%s, %f, %f, %f, region=%s, iseq=%d' % (self.starttime,self.latitude,self.longitude,self.depth, self.region, self.iseq)

class station(db.Model):
    __tablename__ = 'tremor_sta'
    __bind_key__  = 'tremor'

    evid      = db.Column(db.Integer, db.ForeignKey('tremor_catalog.evid'), primary_key=True)
    sta       = db.Column(db.String(5))
    chan      = db.Column(db.String(3))
    #net       = db.Column(db.String(2))
    #loc       = db.Column(db.String(2))
    #envrms    = db.Column(db.Float)
    #maxamp    = db.Column(db.Float)
    #ampunits  = db.Column(db.String(10))
    #peakFreq  = db.Column(db.Float)
    #freqRatio = db.Column(db.Float)
    #f1        = db.Column(db.Float)
    #f2        = db.Column(db.Float)
    staKey    = db.Column(db.Integer, primary_key=True)
    chanKey   = db.Column(db.Integer, primary_key=True)
    #rd        = db.Column(db.Float)
    #weight    = db.Column(db.Float)

    def __repr__(self):
        return '%d, %s, %s' % (self.evid, self.sta, self.chan)
