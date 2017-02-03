#!/usr/bin/env python3
import boto3
from collections import Counter, defaultdict
import redis

SIZE = "__size__"

def get_fancy_dict():
    ret = defaultdict(get_fancy_dict)
    ret[SIZE] = 0
    return ret

def add_folder_sizes(name, tree, bucket_name, p, level):
    set_key = "{bucket}:levels:{level}".format(bucket=bucket_name, level=level)
    p.zadd(set_key, tree[SIZE], name)
    for node_name, tree_node in tree.items():
        if node_name != SIZE:
            full_name = "{}/{}".format(name, node_name)
            add_folder_sizes(full_name, tree_node, bucket_name, p, level+1)

r = redis.StrictRedis()

# TODO: Add dev and production when we are ready for them
profiles = ["staging"]
for profile in profiles:
    session = boto3.Session(profile_name=profile)
    s3 = session.resource('s3')
    bucket_name = "rsyslog-archives-stg" #TODO: change this to retrieve all bucket names
    bucket = s3.Bucket(bucket_name)
    bucket_tree = get_fancy_dict()
    for obj in bucket.objects.all():
        curr_node = bucket_tree
        folders = obj.key.split('/')[:-1]
        bucket_tree[SIZE] += obj.size
        for folder in folders:
            curr_node = curr_node[folder]
            curr_node[SIZE] += obj.size
    r.zadd("buckets", bucket_tree[SIZE], bucket_name)
    p = r.pipeline()
    add_folder_sizes(bucket_name, bucket_tree, bucket_name, p, 0)
    p.execute()

