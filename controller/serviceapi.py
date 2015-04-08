from flask import url_for
from flask.ext.restful import Resource

class ServiceAPI(Resource):
    def get(self):
        return { 'ASH_URL': url_for('ash'),
                 'EDXRF_URL': url_for('edxrf'),
                 'INCOMPATIBLES_URL': url_for('incompatibles'),
                 'LOGS_URL': url_for('logs'),
                 'MGOSYSTEMATICS_URL': url_for('mgosys'),
                 'MAGMATICSULFUR_URL': url_for('magmaticsulfur'),
                 'RSAM_URL': url_for('rsam'),
                 'TREMOR_URL': url_for('tremor'),
                 'LAVALEVEL_URL': url_for('lavalevel'),
                 'TILT_URL': url_for('tilt') }, 200
