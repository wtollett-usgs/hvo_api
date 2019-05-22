import sys

sys.path.append('/app/hvo_api')

from valverest import create_app
application = create_app(env='prod')
