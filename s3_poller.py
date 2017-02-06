#!/usr/bin/env python3
import boto3
from collections import Counter, defaultdict
from functools import partial
from multiprocessing import Pool
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

def store_bucket_data(bucket_name, profile="dev"):
    p = redis.StrictRedis().pipeline()
    session = boto3.Session(profile_name=profile)
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)
    print(bucket_name, end='', flush=True)
    bucket_tree = get_fancy_dict()
    for obj in bucket.objects.all():
        curr_node = bucket_tree
        folders = obj.key.split('/')[:-1]
        bucket_tree[SIZE] += obj.size
        for folder in folders:
            curr_node = curr_node[folder]
            curr_node[SIZE] += obj.size
    p.zadd("buckets", bucket_tree[SIZE], bucket_name)
    add_folder_sizes(bucket_name, bucket_tree, bucket_name, p, 0)
    p.execute()
    print("   DONE")

r = redis.StrictRedis()

# TODO: Add dev and production when we are ready for them
def main():
    pool = Pool()
    profiles = ["dev", "staging", "production"]
    for profile in profiles:
        store_bucket_fun = partial(store_bucket_data, profile=profile)
        session = boto3.Session(profile_name=profile)
        s3 = session.resource('s3')
        # becuase iterables
        bucket_names = map(lambda x: x.name, s3.buckets.all())
        pool.map(store_bucket_fun, bucket_names)
'''
        for bucket in s3.buckets.all():
            store_bucket_data(bucket)
'''

def get_specific_bucket(bucket_name, profile):
    session = boto3.Session(profile_name=profile)
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)
    store_bucket_data(bucket)

main()
