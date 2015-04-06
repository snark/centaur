from six.moves import html_entities
import re
import datetime


ENTITY_MAPPINGS = html_entities.name2codepoint
del ENTITY_MAPPINGS['quot']
del ENTITY_MAPPINGS['lt']
del ENTITY_MAPPINGS['gt']
del ENTITY_MAPPINGS['amp']


def _entity_replace(matchobj):
    trimmed = matchobj.group(0)[1:-1]
    if trimmed in ENTITY_MAPPINGS:
        return '&#{};'.format(ENTITY_MAPPINGS[trimmed])
    else:
        # Throw up our hands in despair
        return trimmed


def entity_names_to_codepoints(content):
    for ename in ENTITY_MAPPINGS:
        content = re.sub(r'&{};'.format(ename), _entity_replace, content)
    return content


def entry_guarantee_date(entry, fallback_date=None):
    date = None
    if entry.published():
        date = entry.published()
    elif entry.updated():
        date = entry.updated()
    elif fallback_date:
        date = fallback_date
    else:
        date = datetime.datetime.now().isoformat()
    return date


def always(node):
    return True


def never(node):
    return False
