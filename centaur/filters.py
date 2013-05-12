import re
import datetime


def any_of(**kwargs):
    filters = kwargs['filters']
    # NB
    # When we begin inflating filters out of configs, we'll want
    # to inflate each filter here.

    def filter(entry):
        filter_passed = False
        for f in filter:
            if f(entry):
                filter_passed = entry
                break
        return filter_passed
    return filter


def all_of(**kwargs):
    filters = kwargs['filters']
    # NB
    # When we begin inflating filters out of configs, we'll want
    # to inflate each filter here.

    def filter(entry):
        filter_passed = False
        for f in filter:
            entry = f(entry)
            if not entry:
                break
        return entry
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
