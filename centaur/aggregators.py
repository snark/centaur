from .util import (generate_feed, validate_feed_settings)
import io


def simple_file(filename=None, max_results=10, feed_settings=None):
    if not filename:
        raise TypeError('file_aggregator() requires filename argument')
    if not feed_settings:
        feed_settings = {}
    validate_feed_settings(feed_settings)
    entries = []
    try:
        while True:
            entry, context = yield
            entries.append(entry)
    except GeneratorExit:
        entries.sort(reverse=True,
                     key=lambda e:
                     e.get('updated_parsed', e.get('created_parsed')))
        new_feed = generate_feed(entries, settings=feed_settings)
        with io.open(filename, mode='w', encoding='utf-8') as f:
            f.write(new_feed.to_string())
