import os
import rq
import sys
import logging
import redis
import psycopg2
from flask import Flask
from worker import conn

# Set module name
__module__ = 'teamdict'

# Initialize flask app
app = Flask(__name__, static_folder=None)
app.config.update({
    'SIGNING_SECRET': os.environ.get('SIGNING_SECRET'),
    'REDIS_URL': os.environ.get('REDIS_URL','redis://'),
    'DATABASE_URL': os.environ.get('DATABASE_URL')
})
app.task_queue = rq.Queue(connection=conn)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.dbconn = psycopg2.connect(app.config['DATABASE_URL'], sslmode='require')

# Set up database table for mass data entry
with app.dbconn.cursor() as cur:
    query = ('CREATE TABLE IF NOT EXISTS data_entry_queue (' +
            'url_ext VARCHAR PRIMARY KEY, ' +
            'table_name VARCHAR, ' +
            'response_url VARCHAR, ' +
            "'exp_date TIMESTAMP NOT NULL DEFAULT now() + interval '5 minutes'" +
            ');')
    cur.execute(query)
    conn.commit()

# Allow app to find @app.route views
from teamdict import views
