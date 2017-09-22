# Running from bash with flask:
#
# FLASK_APP=sign.py FLASK_DEBUG=1 flask run --host=0.0.0.0

from flask import Flask, request, render_template, jsonify
import configparser
import logging
import requests
import json
import hashlib

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('wsgi_apps.conf')

MAC_FILE = config['sign']['mac_file']
IMAGE_URL = config['sign']['image_url']
BASE_URL = config['sign']['base_url']
AUTH_USER = config['sign']['auth_user']
AUTH_PASS = config['sign']['auth_pass']

logging.basicConfig(filename=__name__ + '.log', level=logging.INFO)

with open(MAC_FILE) as f:
    macs = json.load(f)


@app.route('/view/<mac>')
def route_view(mac):
    """get a list of slides for a branch"""
    details = True if request.args.get('details') else False
    branch = macs[mac] if mac in macs else None
    slides = get_slides(branch)
    slides_hash = hash_slides(slides)
    return render_template('sign.html', mac=mac, branch=branch, slides=slides,
                           details=details, slides_hash=slides_hash)


@app.route('/hash/<mac>')
def route_hash(mac):
    branch = macs[mac] if mac in macs else None
    return jsonify(hash_slides(get_slides(branch)))


def get_slides(branch):
    if branch is None:
        return {}
    r = requests.get(BASE_URL + '/rest/taxonomy_term?parameters[name]=' +
                     branch, auth=(AUTH_USER, AUTH_PASS))
    tid = r.json()[0]['tid']
    nodes = requests.post(BASE_URL + '/rest/taxonomy_term/selectNodes',
                          auth=(AUTH_USER, AUTH_PASS), json={'tid': tid})
    slides = []
    for n in nodes.json():
        s = {}
        s['title'] = n['title']
        s['changed_time'] = n['changed']
        s['image_filename'] = n['field_slide_image']['und'][0]['filename']
        s['image_url'] = IMAGE_URL + '/' + s['image_filename']
        s['duration'] = n['field_duration']['und'][0]['value']
        slides.append(s)
    return slides


def hash_slides(s):
    h = hashlib.md5(json.dumps(s, sort_keys=True).encode('utf-8')).hexdigest()
    return {'value': h}
