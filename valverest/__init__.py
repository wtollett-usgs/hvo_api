import logging

from flask import Flask
from flask_restful import Api
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
from controller.magmaticsulfurapi import MagmaticSulfurAPI
from controller.mgosystematicsapi import MgOSystematicsAPI
from controller.npsadvisoryapi import NPSAdvisoryAPI
from controller.rsamapi import RSAMAPI
from controller.rtnetapi import RTNetAPI
from controller.serviceapi import ServiceAPI
from controller.so2emissionsapi import SO2EmissionsAPI
from controller.so2highresapi import SO2HighResAPI
from controller.strainapi import StrainAPI
from controller.tiltapi import TiltAPI
from controller.tremorapi import TremorAPI
from controller.triggersapi import TriggersAPI
from valverest.database import (
    db, db2, db3, db4, db5, db6,
    db7, db8, db9, db10, db11, db12
)


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
    db9.init_app(app)
    db10.init_app(app)
    db11.init_app(app)
    db12.init_app(app)
    api.add_resource(ServiceAPI, '/', '/api')
    api.add_resource(AshAPI, '/api/ash', endpoint='ash')
    api.add_resource(EDXRFAPI, '/api/edxrf', endpoint='edxrf')
    api.add_resource(FlyspecAPI, '/api/flyspec', endpoint='flyspec')
    api.add_resource(FileAPI, '/api/file', endpoint='file')
    api.add_resource(GPSAPI, '/api/gps', endpoint='gps')
    api.add_resource(HypocenterAPI, '/api/hypocenter', endpoint='hypocenter')
    api.add_resource(IncompatiblesAPI, '/api/incompatibles',
                     endpoint='incompatibles')
    api.add_resource(LaserLavaLevelAPI, '/api/laserlavalevel',
                     endpoint='laserlavalevel')
    api.add_resource(LavaLevelAPI, '/api/lavalevel', endpoint='lavalevel')
    api.add_resource(LogsAPI, '/api/logs', endpoint='logs')
    api.add_resource(MagmaticSulfurAPI, '/api/magmaticsulfur',
                     endpoint='magmaticsulfur')
    api.add_resource(MgOSystematicsAPI, '/api/mgosys', endpoint='mgosys')
    api.add_resource(NPSAdvisoryAPI, '/api/npsadvisory',
                     endpoint='npsadvisory')
    api.add_resource(RSAMAPI, '/api/rsam', endpoint='rsam')
    api.add_resource(RTNetAPI, '/api/rtnet', endpoint='rtnet')
    api.add_resource(SO2EmissionsAPI, '/api/so2emissions',
                     endpoint='so2emissions')
    api.add_resource(SO2HighResAPI, '/api/so2highres', endpoint='so2highres')
    api.add_resource(StrainAPI, '/api/strain', endpoint='strain')
    api.add_resource(TiltAPI, '/api/tilt', endpoint='tilt')
    api.add_resource(TremorAPI, '/api/tremor', endpoint='tremor')
    api.add_resource(TriggersAPI, '/api/triggers', endpoint='triggers')
    logging.basicConfig(filename='%s' % app.config['LOGFILE'],
                        level=logging.DEBUG)
    return app
