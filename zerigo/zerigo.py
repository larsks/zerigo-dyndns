#!/usr/bin/env python

import os
import sys
import requests
from lxml import etree

Z_API_ROOT='http://ns.zerigo.com/api/1.1'

class APIError(Exception):
    def __init__(self, message, response=None):
        self.response = response
        super(APIError, self).__init__(message)

class AuthenticationError(APIError):
    pass

def unserialize(ele, top=False):
    if ele.get('type') == 'array':
        v = []
        for c in ele.iterchildren():
            v.append(unserialize(c))

        if top:
            return {ele.tag: v}
        else:
            return v
    elif ele.get('nil'):
        return None
    elif ele.get('type') == 'datetime':
        return ele.text
    elif ele.get('type') == 'integer':
        return int(ele.text)
    elif ele.get('type') == 'boolean':
        return ele.text.strip() == 'true'
    elif len(ele):
        v = {}
        for c in ele.iterchildren():
            v[c.tag] = unserialize(c)
        return v
    else:
        return ele.text.strip() if ele.text else ''

def serialize(root, data):
    pass

class Zerigo (object):
    def __init__ (self, username, apikey):
        self.config = config

        self.api_root = Z_API_ROOT

        self.session = requests.Session()
        self.session.auth = (username, apikey)

    def put(self, url, data, **kwargs):
        xml = serialize(data)

    def get(self, url, **kwargs):
        url = '%s/%s' % (Z_API_ROOT, url)

        r = self.session.get(url, params=kwargs)

        if not r:
            if r.status_code == 401:
                raise AuthenticationError(url, response=r)
            else:
                raise APIError(url, response=r)

        return unserialize(etree.fromstring(str(r.text)))

    def zones(self, **kwargs):
        return self.get('zones.xml', **kwargs)

    def zone(self, zid, **kwargs):
        return self.get('zones/%s.xml' % (zid), **kwargs)

    def zonestats(self, zid, **kwargs):
        return self.get('zones/%s/stats.xml' % (zid), **kwargs)

    def hosts(self, zid, **kwargs):
        return self.get('zones/%s/hosts.xml' % (zid), **kwargs)

    def host(self, hid, **kwargs):
        return self.get('hosts/%s.xml' % (hid), **kwargs)

    def public_ip_v4(self, **kwargs):
        return self.get('tools/public_ipv4.xml', **kwargs)

    def public_ip_v6(self, **kwargs):
        return self.get('tools/public_ipv6.xml', **kwargs)

if __name__ == '__main__':

    import yaml
    config = yaml.load(open('zerigo.conf'))
    z = Zerigo(
            config['zerigo']['username'],
            config['zerigo']['api key'],
            )
    zones = z.zones()

