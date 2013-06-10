import re
import datetime
from .util import (inflate_filter)


def any_of(**kwargs):
    filters = kwargs['filters']
    # filter values might be:
    # * a dict, with the filter name the key and the settings dict the val
    # * a string
    # * fully inflated filters
    inflated = [
        inflate_filter(f) if not isinstance(f, dict)
        else inflate(f.keys()[0], f.items()[0])
        for f in filters
    ]

    def filter(entry):
        filter_passed = False
        for f in inflated:
            if f(entry):
                filter_passed = entry
                break
        return filter_passed
    return filter


def all_of(**kwargs):
    filters = kwargs['filters']
    # filter values might be:
    # * a dict, with the filter name the key and the settings dict the val
    # * a string
    # * fully inflated filters
    inflated = [
        inflate_filter(f) if not isinstance(f, dict)
        else inflate(f.keys()[0], f.items()[0])
        for f in filters
    ]

    def filter(entry):
        filter_passed = False
        for f in filter:
            entry = f(entry)
            if not entry:
                break
        return entry if entry else False
    return filter


def normalize_time(**kwargs):
    def filter(entry):
        if 'created_parsed' in entry:
            c = entry['created_parsed'][0:6]
            created = dateime.datetime(*c)
            entry['created'] = created.strftime('%Y-%m-%dT%H:%M:%SZ')
        if 'updated_parsed' in entry:
            u = entry['updated_parsed'][0:6]
            updated = datetime.datetime(*u)
            entry['updated'] = updated.strftime('%Y-%m-%dT%H:%M:%SZ')
        return entry
    return filter


def title_matches(**kwargs):
    def filter(entry):
        regexes = kwargs.get('regexes', [])
        strings = kwargs.get('strings', [])
        filter_passed = False
        for string in strings:
            if string.lower() in entry['title'].lower():
                filter_passed = True
                break
        if not filter_passed:
            for pattern in regexes:
                if re.search(pattern, entry['title'], re.IGNORECASE):
                    filter_passed = True
                    break
        return entry if filter_passed else False
    return filter
