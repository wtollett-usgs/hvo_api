#!/bin/bash
mod_wsgi-express start-server /app/hvo_api/run.wsgi \
    --port=80 --user=apache --group=www --document-root /app/hvo_api \
    --processes=1 --threads=5