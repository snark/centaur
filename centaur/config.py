import json
import os.path
import xml.etree.ElementTree as ET

from .util import validate_feed_settings

CONFIG_KEYS = ('feeds', 'filters', 'aggregators')


def load(config_file_path):
    # a json config has six keys at the moment
    # - a list of feeds
    # - a list of (universally applied) filters
    # - a list of aggregators
    # an opml config only has one
    # - a list of feeds
    config_fileext = os.path.splitext(config_file_path)[1]
    if config_fileext not in ('.json', '.opml'):
        raise TypeError(
            'You passed in a filetype we don\'t understamd: {}'.format(
                config_fileext
            )
        )
    config_dict = {}
    with open(config_file_path) as f:
        config_string = f.read()
    if config_fileext == '.json':
        orig_dict = json.loads(config_string)
        for x in CONFIG_KEYS:
            if x in orig_dict:
                config_dict[x] = orig_dict[x]
    elif config_fileext == '.opml':
        root = ET.fromstring(config_string)
        body = root.find('body')
        outlines = body.findall('outline')
        config_dict = {}
        config_dict['feeds'] = [x.attrib['xmlUrl'] for x in outlines]
    return config_dict
