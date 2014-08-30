# -*- coding: utf-8 -*-

import logging
import functools 
import signal

from boto.s3.connection  import  S3Connection
from boto.exception import S3CreateError

from pyS3fs.config import config

# Dirty hack so that "/" won't mess up the ls command.
# As of now, all keys are treated as files and there is
# no concept of directories.
SLASH_PLACEHOLDER = u"__SLASH__"

class S3BucketAlreadyExistsException(Exception):
    pass


class S3TimeoutException(Exception):
    pass

# Decorator for setting custom timeout for http(s) calls, since
# boto only accepts timeout through it's own configuration
# Cool ideia but only works in main thread
HTTP_REQUEST_TIMEOUT = 1
def timeout_watcher(timeout_in_seconds=HTTP_REQUEST_TIMEOUT):
    def timeout_handler(signum, frame):
        raise S3TimeoutException

    def actual_decorator(function):
        @functools.wraps(function)
        def decorate(*args, **kwargs):
            print "I'm decorated"
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_in_seconds)
            function(*args, **kwargs)
            signal.alarm(0)
        return decorate
    return actual_decorator


class S3Client(object):
    def __init__(self):
        print "Creating client"
        self._connect(config["aws_key"], config["aws_secret"])
        self._get_or_create_bucket(config["aws_bucket_name"])

    def put_file(self, key_name, data):
        self.bucket.new_key(key_name).set_contents_from_string(data)

    def get_file(self, key_name):
        key_name = key_name.replace(SLASH_PLACEHOLDER, u"/")
        return self.bucket.get_key(key_name).get_contents_as_string()

    def list_files(self):
        return [key.name.replace("/", SLASH_PLACEHOLDER)
                for key in self.bucket.get_all_keys()]

    def _connect(self, aws_key, aws_secret):
        print "Connecting"
        self.conn = S3Connection(aws_key, aws_secret)
        print "Connected"

    def _get_or_create_bucket(self, bucket_name):
        print "Will create bucket"
        self.bucket = self.conn.lookup(bucket_name)
        if not self.bucket:
            try:
                self.bucket = self.conn.create_bucket(bucket_name)
            except S3CreateError:
                logging.error("A bucket with that name already exists. Choose" \
                    " another name and change your config file")
                raise S3BucketAlreadyExistsException()

        print "Got bucket"
