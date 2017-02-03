#!/usr/bin/env python3
import boto3
import redis

r = redis.StrictRedis()

# TODO: Add dev and production when we are ready for them
profiles = ["staging"]
for profile in profiles:
    session = boto3.Session(profile_name=profile)
    s3 = session.resource('s3')
    bucket_name = "rsyslog-archives-stg" #TODO: change this to retrieve all bucket names
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.all():
        key = bucket_name + "/" + obj.key
        r.set(key, obj.size)
