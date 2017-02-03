#!/usr/bin/env python
from flask import Flask, jsonify, request
from flask_cors import CORS
import redis
import flask

app = Flask(__name__, template_folder='./')
CORS(app)
r = redis.StrictRedis()

def get_bucket_size(bucket_name):
    return int(r.zscore("buckets", bucket_name))

def get_all_buckets():
    return r.zrevrange("buckets", 0, -1, withscores=True)

def name_score_pair_to_dict(pair):
    return {'name': pair[0].decode('UTF-8'), 'size': int(pair[1])}

@app.route('/buckets')
@app.route('/buckets/')
def get_buckets():
    return jsonify([name_score_pair_to_dict(p) for p in get_all_buckets()])

@app.route('/buckets/<name>')
@app.route('/buckets/<name>/')
def get_bucket(name):
    return jsonify({'name': name, 'size': get_bucket_size(name)})

def get_folders_at_level(bucket_name, level):
    key = "{}:levels:{}".format(bucket_name, level)
    return r.zrevrange(key, 0, -1, withscores=True)

@app.route('/buckets/<name>/folders')
@app.route('/buckets/<name>/folders/')
def get_folders(name):
    level = request.args.get('level', 1)
    return jsonify([name_score_pair_to_dict(p) for p in get_folders_at_level(name, level)])

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/<path:path>")
def send_current(path):
    return flask.send_from_directory("./", path)


@app.route("/node_modules/<path:path>")
def send_modules(path):
    return flask.send_from_directory("node_modules", path)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
