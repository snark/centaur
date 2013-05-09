import pyatom
import datetime
import json

def inflate_filter(factory, settings_dict) {
    return factory(*settings_dict)

def validate_feed_settings(setting_dict):
    required = ['title', 'feed_url', 'url']
    missing = []
    if not hasattr(setting_dict, 'get'):
        raise ValueError('Cannot evaluate non-dictlike settings')
    for prop in required:
        if not setting_dict.get(prop):
            missing.append(prop)
    if missing:
        raise KeyError(
            'Required setting values missing: {}'.format(
                ', '.join(missing)
            )
        )


def generate_feed(entries, settings=None):
    if not settings:
        settings = {}
    validate_feed_settings(settings)
    feed = pyatom.AtomFeed(
        title=settings['title'],
        subtitle=settings.get('subtitle'),
        feed_url=settings['feed_url'],
        url=settings['url'],
    )
    for e in entries:
        feed.add(
            title=e['title'],
            author=e['author'],
            content=e['content'][0]['value'],
            id=e['id'],
            updated=datetime.datetime(*(e['updated_parsed'][0:6]))
        )
    return feed
