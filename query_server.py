from flask import Flask, jsonify
import redis

app = Flask(__name__)
r = redis.StrictRedis()

def get_bucket_size(bucket_name):
    total_size = 0
    for key in r.scan_iter(match="{}/*".format(bucket_name)):
         total_size += int(r.get(key))
    return total_size
    

@app.route('/buckets')
def get_buckets():
    pass

@app.route('/buckets/<name>')
def get_bucket(name):
    return jsonify({'name': name, 'size': get_bucket_size(name)})

@app.route('/buckets/<name>/folders')
def get_folders(name):
    pass

if __name__ == "__main__":
    app.run()
