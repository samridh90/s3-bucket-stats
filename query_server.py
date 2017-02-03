#!/usr/bin/env python3
from flask import Flask, jsonify, request
import redis

app = Flask(__name__)
r = redis.StrictRedis()

def get_bucket_size(bucket_name):
    return int(r.zscore("buckets", bucket_name))

def get_all_buckets():
    return r.zrevrange("buckets", 0, -1, withscores=True)

def name_score_pair_to_dict(pair):
    return {'name': pair[0].decode('UTF-8'), 'size': int(pair[1])}

@app.route('/buckets')
def get_buckets():
    return jsonify([name_score_pair_to_dict(p) for p in get_all_buckets()])

@app.route('/buckets/<name>')
def get_bucket(name):
    return jsonify({'name': name, 'size': get_bucket_size(name)})

def get_folders_at_level(bucket_name, level): 
    key = "{}:levels:{}".format(bucket_name, level)
    return r.zrevrange(key, 0, -1, withscores=True)

@app.route('/buckets/<name>/folders')
def get_folders(name):
    level = request.args.get('level', 1)
    return jsonify([name_score_pair_to_dict(p) for p in get_folders_at_level(name, level)])

if __name__ == "__main__":
    app.run()
