from flask import url_for
from flask_restful import Resource

class ServiceAPI(Resource):
    def get(self):
        return { 'ASH_URL': url_for('ash'),
                 'EDXRF_URL': url_for('edxrf'),
                 'INCOMPATIBLES_URL': url_for('incompatibles'),
                 'LOGS_URL': url_for('logs'),
                 'MGOSYSTEMATICS_URL': url_for('mgosys'),
                 'MAGMATICSULFUR_URL': url_for('magmaticsulfur'),
                 'RSAM_URL': url_for('rsam'),
                 'STRAIN_URL': url_for('strain'),
                 'TREMOR_URL': url_for('tremor'),
                 'LAVALEVEL_URL': url_for('lavalevel'),
                 'TILT_URL': url_for('tilt'),
                 'FLYSPEC_URL': url_for('flyspec'),
                 'HYPOCENTER_URL': url_for('hypocenter') }, 200
