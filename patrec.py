# Running from bash with flask:
#
# FLASK_APP=patrec.py FLASK_DEBUG=1 flask run

from flask import Flask, request, render_template
import configparser
import logging
import requests

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('wsgi_apps.conf')

API_URL_BARCODE = config['patrec']['api_url_barcode']

logging.basicConfig(filename=__name__ + '.log', level=logging.INFO)


@app.route('/', methods=['GET'])
def index():
    """Serve index page"""
    return render_template('patrec.html')


@app.route('/', methods=['POST'])
def index_submit():
    """Process a submitted form input and serve result"""
    f = [s for s in request.form['barcodes'].splitlines() if s]
    return render_template('patrec.html', records=get_records(f))


def get_records(barcodes):
    """Return a list of patron records, given a list of barcodes"""
    r = []
    for i, b in enumerate(barcodes):
        if len(b) is not 14:
            e = "Barcode {} has length {} (should be 14)".format(b, len(b))
            return ["Error: {}".format(e)]
        logging.info('gathering data for barcode {} [{}/{}]'
                     .format(b, i+1, len(barcodes)))
        r.extend(['{}|p{}'.format(b, s) for s in get_patron_record(b)])
    return r


def get_patron_record(b):
    """Return the record number(s) for the given barcode number."""
    r = requests.get(API_URL_BARCODE + str(b) + "/dump")  # Get from server
    r.raise_for_status()
    t = r.text.splitlines()
    m = [s for s in t if "RECORD #" in s]
    x = [s.replace('<BR>', '').split('=')[1] for s in m]
    return x
