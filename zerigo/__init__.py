#!/usr/bin/env python

import os
import sys
import urllib2
import configobj

from lxml import etree

Z_API_ROOT='http://ns.zerigo.com/api/1.1'

class Zerigo (object):
    def __init__ (self, config):
        self.config = config

        self.api_root = config['zerigo'].get('api_root', Z_API_ROOT)
        self.api_user = config['zerigo']['api_user']
        self.api_pass = config['zerigo']['api_key']

        self.auth_handler = urllib2.HTTPBasicAuthHandler()
        self.auth_handler.add_password(
                realm = 'Application',
                uri = 'http://ns.zerigo.com/',
                user = self.api_user,
                passwd = self.api_pass)
        self.opener = urllib2.build_opener(self.auth_handler)

    def get_host_in_zone(self, zone, host):
        zonedata = self.get_zone(zone)
        hostdata = zonedata.xpath('//host[hostname="%s" and host-type="A"]'
                % host)
        return hostdata

    def get_zone(self, zone):
        url = '/'.join([self.api_root, 'zones', '%s.xml' % zone])
        fd = self.opener.open(url)
        return etree.parse(fd)

    def update_address(self, zone, host, ipaddr):
        hostdata = self.get_host_in_zone(zone, host)[0]
        id = hostdata.find('id').text
        hostdata.find('data').text = ipaddr
        url = '/'.join([self.api_root, 'hosts', '%s.xml' % id])
        self.PUT(url, etree.tostring(hostdata))

    def PUT (self, url, data):
        request = urllib2.Request(url, data=data)
        request.add_header('Content-type', 'text/xml')
        request.get_method = lambda: 'PUT'
        fd = self.opener.open(request)
        return fd.read()
        
if __name__ == '__main__':

    z = Zerigo(configobj.ConfigObj('zerigo.conf'))

