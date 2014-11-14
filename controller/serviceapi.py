from flask import url_for
from flask.ext.restful import Resource

class ServiceAPI(Resource):
    def get(self):
        return { 'ASH_URL': url_for('ash'),
                 'EDXRF_URL': url_for('edxrf'),
                 'INCOMPATIBLES_URL': url_for('incompatibles'),
                 'LOGS_URL': url_for('logs'),
                 'MGOSYSTEMATICS_URL': url_for('mgosys'),
                 'MAGMATICSULFUR_URL': url_for('magmaticsulfur') }, 200
