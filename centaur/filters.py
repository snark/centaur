import re


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
