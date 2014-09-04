# -*- coding: utf-8 -*-


class InvalidCacheType(Exception):
    pass


class CacheType(object):
    UPSTREAM = "upstream"
    DOWNSTREAM = "downstream"


class Cache(object):
    def __init__(self, cache_type, data=""):

        if cache_type not in [CacheType.DOWNSTREAM, CacheType.UPSTREAM]:
            raise InvalidCacheType

        self.cache_type = cache_type
        self.data = data

    def append_data(self, data):
        self.data += data
