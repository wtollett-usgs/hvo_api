from flask import Flask
from flask.ext.restful import Api
from flask.ext.sqlalchemy import SQLAlchemy
from controller.edxrfapi import EDXRFAPI
from controller.serviceapi import ServiceAPI
from controller.ashapi import AshAPI
from controller.incompatiblesapi import IncompatiblesAPI
from controller.mgosystematicsapi import MgOSystematicsAPI
from controller.magmaticsulfurapi import MagmaticSulfurAPI
from controller.lavalevelapi import LavaLevelAPI
from controller.logsapi import LogsAPI
from controller.rsamapi import RSAMAPI
from controller.tremorapi import TremorAPI
from valverest.database import db, db2, db3, db4, db5
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
    api.add_resource(ServiceAPI, '/', '/api')
    api.add_resource(AshAPI, '/api/ash', endpoint = 'ash')
    api.add_resource(EDXRFAPI, '/api/edxrf', endpoint = 'edxrf')
    api.add_resource(IncompatiblesAPI, '/api/incompatibles', endpoint = 'incompatibles')
    api.add_resource(LavaLevelAPI, '/api/lavalevel', endpoint = 'lavalevel')
    api.add_resource(LogsAPI, '/api/logs', endpoint = 'logs')
    api.add_resource(MagmaticSulfurAPI, '/api/magmaticsulfur', endpoint = 'magmaticsulfur')
    api.add_resource(MgOSystematicsAPI, '/api/mgosys', endpoint = 'mgosys')
    api.add_resource(RSAMAPI, '/api/rsam', endpoint = 'rsam')
    api.add_resource(TremorAPI, '/api/tremor', endpoint = 'tremor')
    logging.basicConfig(filename='%s' % app.config['LOGFILE'], level=logging.DEBUG)
    return app
