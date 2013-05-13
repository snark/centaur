#!/usr/bin/env python

import argparse
import os
import sys

from centaur import (config, parser, filters, aggregators, util)


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('config', nargs='+',
        help='full path to config file')
    parser.add_argument('-f', '--feed', action='append', 
            help='a feed to include')
    args = parser.parse_args()
    cnf = {}
    try:
        for c in args.config:
            config_dict = config.load(c)
            for key in config_dict:
                if key not in cnf:
                    cnf[key] = config_dict[key]
                elif key !='feeds' and cnf[key] != config_dict[key]:
                    sys.exit('You specified multiple actions for {}! '
                        'Please specify only one.'.format(key))
                elif key == 'feeds':
                    cnf[key].extend(config_dict[key])
    except Exception as e:
        raise
        sys.exit('Something went wrong:\n {}'.format(e))
    if args.feed:
        print cnf['feeds']
        feedlist = list(set(cnf['feeds'] + args.feed))
        for f in feedlist:
            print f
        cnf['feeds'] = feedlist
    if 'aggregators' not in cnf:
        sys.exit('You didn\'t specify any aggregators!')
    if 'filters' in cnf:
        try:
            filters = [
                util.inflate_filter(k, v) for k, v in cnf['filters'].items()
            ]
        except Exception as e:
            sys.exit('Could not inflate filters!\n{}'.format(e))
    try:
        aggregators = [
            util.inflate_aggregator(k, v) for k, v in cnf['aggregators'].items()
        ]
    except Exception as e:
        sys.exit('Could not inflate aggregators!\n{}'.format(e))
    try:
        for a in aggregators:
            # Pump to prime
            next(a) 
        for f in cnf['feeds']:
            parser.parse_feed(f, aggregators=aggregators, filters=filters)
        for a in aggregators:
            a.close()
    except Exception as e:
        sys.exit('Something went wrong!\n{}'.format(e))

if __name__ == '__main__':
    main()

