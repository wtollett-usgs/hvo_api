from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from controller.ashapi import AshAPI
from controller.edxrfapi import EDXRFAPI
from controller.fileapi import FileAPI
from controller.flyspecapi import FlyspecAPI
from controller.gpsapi import GPSAPI
from controller.hypocenterapi import HypocenterAPI
from controller.incompatiblesapi import IncompatiblesAPI
from controller.laserlavalevelapi import LaserLavaLevelAPI
from controller.lavalevelapi import LavaLevelAPI
from controller.logsapi import LogsAPI
from controller.mgosystematicsapi import MgOSystematicsAPI
from controller.magmaticsulfurapi import MagmaticSulfurAPI
from controller.rsamapi import RSAMAPI
from controller.serviceapi import ServiceAPI
from controller.strainapi import StrainAPI
from controller.tiltapi import TiltAPI
from controller.tremorapi import TremorAPI
from valverest.database import db, db2, db3, db4, db5, db6, db7, db8
import logging

def create_app(*args, **kwargs):
    env = kwargs['env']
    app = Flask(__name__)
    app.config.from_object('conf.%s' % env)
    api = Api(app)
    db.init_app(app)
    db2.init_app(app)
    db3.init_app(app)
    db4.init_app(app)
    db5.init_app(app)
    db6.init_app(app)
    db7.init_app(app)
    db8.init_app(app)
    api.add_resource(ServiceAPI, '/', '/api')
    api.add_resource(AshAPI, '/api/ash', endpoint = 'ash')
    api.add_resource(EDXRFAPI, '/api/edxrf', endpoint = 'edxrf')
    api.add_resource(FlyspecAPI, '/api/flyspec', endpoint = 'flyspec')
    api.add_resource(GPSAPI, '/api/gps', endpoint = 'gps')
    api.add_resource(HypocenterAPI, '/api/hypocenter', endpoint = 'hypocenter')
    api.add_resource(IncompatiblesAPI, '/api/incompatibles', endpoint = 'incompatibles')
    api.add_resource(FileAPI, '/api/file', endpoint = 'file')
    api.add_resource(LaserLavaLevelAPI, '/api/laserlavalevel', endpoint='laserlavalevel')
    api.add_resource(LavaLevelAPI, '/api/lavalevel', endpoint = 'lavalevel')
    api.add_resource(LogsAPI, '/api/logs', endpoint = 'logs')
    api.add_resource(MagmaticSulfurAPI, '/api/magmaticsulfur', endpoint = 'magmaticsulfur')
    api.add_resource(MgOSystematicsAPI, '/api/mgosys', endpoint = 'mgosys')
    api.add_resource(RSAMAPI, '/api/rsam', endpoint = 'rsam')
    api.add_resource(StrainAPI, '/api/strain', endpoint = 'strain')
    api.add_resource(TiltAPI, '/api/tilt', endpoint = 'tilt')
    api.add_resource(TremorAPI, '/api/tremor', endpoint = 'tremor')
    logging.basicConfig(filename='%s' % app.config['LOGFILE'], level=logging.DEBUG)
    return app
