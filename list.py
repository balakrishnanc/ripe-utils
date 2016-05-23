#!/usr/bin/env python
# -*- mode: python; coding: utf-8; fill-column: 80; -*-
#
# list.py
# Created by Balakrishnan Chandrasekaran on 2016-05-23 00:42 -0400.
# Copyright (c) 2016 Balakrishnan Chandrasekaran <balac@cs.duke.edu>.
#

"""
list.py
List all RIPE Atlas probes.
"""

__author__  = 'Balakrishnan Chandrasekaran <balac@cs.duke.edu>'
__version__ = '1.0'
__license__ = 'MIT'


import argparse
from datetime import datetime as dt
import io
import requests


API_ROOT = u'https://atlas.ripe.net/api/v2'
API_PROBES = API_ROOT + u'/probes/'

# Number of objects per size.
# NOTE: API does not allow more than 500 objects per page.
PAGE_SZ = 500


# Delimiters.
COL_SEP = u','
TAG_SEP = u'+'


class Tag:
    __slots__ = (u'name', u'slug')

    def __init__(self, name, slug):
        self.name = name
        self.slug = slug


class Status:
    __slots__ = (u'since', u'id', u'name')


    def __init__(self, **kwargs):
        for attrib in self.__slots__:
            setattr(self, attrib, '')

        for k, v in kwargs.items():
            setattr(self, k, v)


class Point:
    """Latitude-longitude coordinate.
    """
    __slots__ = (u'x', u'y', u'lat', u'lng')

    def __init__(self, *coords):
        self.x, self.y = coords
        self.lat, self.lng = self.y, self.x


class Geometry:
    __slots__ = (u'coordinates', u'type')


    def __init__(self, **kwargs):
        for attrib in self.__slots__:
            setattr(self, attrib, '')

        for k, v in kwargs.items():
            setattr(self, k, v)

        if self.coordinates:
            self.coordinates = Point(*self.coordinates)
        else:
            self.coordinates = Point(-1111.0, -1111.0)


class Probe:
    """RIPE Atlas Probe.
    """
    __slots__ = {u'address_v4',
                 u'address_v6',
                 u'asn_v4',
                 u'asn_v6',
                 u'country_code',
                 u'description',
                 u'first_connected',
                 u'geometry',
                 u'id',
                 u'is_anchor',
                 u'is_public',
                 u'last_connected',
                 u'prefix_v4',
                 u'prefix_v6',
                 u'status',
                 u'status_since',
                 u'tags',
                 u'type'}

    def __init__(self, **kwargs):
        """Initialize Probe using the given data.
        """
        for attrib in self.__slots__:
            setattr(self, attrib, '')

        for k, v in kwargs.items():
            setattr(self, k, v)

        if self.status:
            self.status = Status(**self.status)
        else:
            self.status = Status()

        if self.geometry:
            self.geometry = Geometry(**self.geometry)
        else:
            self.geometry = Geometry()

        self.tags = [Tag(t[u'name'], t[u'slug']) for t in self.tags]


def get_probe_data(results):
    """Parse the probe details from the data returned by the API.
    """
    for probe_data in results:
        yield Probe(**probe_data)


def get_probes():
    """Retrieve all RIPE Atlas probes.
    """
    r = requests.get(API_PROBES,
                     params={u'page_size' : PAGE_SZ, u'sort' : u'id'})
    while True:
        if not r.status_code == requests.codes.ok:
            r.raise_for_status()

        data = r.json()
        count = data[u'count']
        url = data[u'next']

        if not count:
            break

        yield from get_probe_data(data[u'results'])

        if not url:
            break

        r = requests.get(url)


def main(args):
    with io.open(args.out_path, 'w', encoding='utf-8') as f:
        # Header.
        f.write(u"#<id>,<asn_v4>,<address_v4>,<pfx_v4>"
                u",<asn_v6>,<address_v6>,<pfx_v6>"
                u",<country>,<lat>,<lng>"
                u",<anchor?>,<public?>,<last_connect>"
                u",<status>,<status_ts>,<tags>\n")

        n = 0
        for p in get_probes():
            f.write(u"%s\n" %
                    COL_SEP.join(str(v) for v in
                                 (p.id,
                                  p.asn_v4,
                                  p.address_v4,
                                  p.prefix_v4,
                                  p.asn_v6,
                                  p.address_v6,
                                  p.prefix_v6,
                                  p.country_code,
                                  p.geometry.coordinates.lat,
                                  p.geometry.coordinates.lng,
                                  1 if p.is_anchor else 0,
                                  1 if p.is_public else 0,
                                  p.last_connected,
                                  p.status.name.upper(),
                                  p.status_since,
                                  TAG_SEP.join(t.slug for t in p.tags))))

            n += 1
            if not n % PAGE_SZ:
                print("- #probes: %d" % (n))
        print("- fetched details of %d probes." % (n))


def __get_parser():
    """Build a parser to parse command-line arguments.
    """
    desc = ("List all RIPE Atlas probes.")
    parser = argparse.ArgumentParser(description = desc)
    parser.add_argument('--version',
                        action = 'version',
                        version = '%(prog)s ' + "%s" % (__version__))
    parser.add_argument('-o', '--output',
                        dest = 'out_path',
                        metavar = 'output',
                        required = True,
                        help = 'Relative/absolute path of output file.')
    return parser


if __name__ == '__main__':
    args = __get_parser().parse_args()
    main(args)
