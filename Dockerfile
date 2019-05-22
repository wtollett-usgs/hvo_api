FROM python:3.6-slim

LABEL maintainer="wtollett@usgs.gov"

RUN apt-get update && apt-get install -y --no-install-recommends \
    apache2 apache2-dev

WORKDIR /app

# Checkout code
COPY hvo_api /app/hvo_api

RUN pip install --no-cache-dir -r /app/hvo_api/requirements.txt

# Create User/Group
RUN groupadd -g 48 apache \
    && useradd -u 48 -g 48 -s /sbin/nologin apache \
    && groupadd -g 2200 www

# Run Server
COPY run.sh .
RUN chown -R apache:www /app/hvo_api && chmod +x run.sh

ARG LU
ARG LP
ENV LOGS_USER=$LU \
    LOGS_PW=$LP

ENTRYPOINT [ "./run.sh" ]