import feedparser
import blinker

def parse_feed(feed_url, filters=None, aggregators=None, cache=None,
        signal_channel='centaur'):
    """
    Parses a feed using the Universal Feed Parser.

    Each entry returned by the UFP will be run through any of the
    filter functions provided. All remaining (and potentially
    tranformed) filters will be returned to the optional aggregators
    provided.
    """

    if not isinstance(filters, list):
        filters = []

    if not isinstance(aggregators, list):
        aggregators = []

    signal = blinker.signal(signal_channel)

    if not isinstance(feed_url, basestring):
        raise ValueException('Feed URL is not a string: {0}'
                .format(str(feed_url)))

    signal.send(
        'parse_begin',
        id=feed_url,
        data=None,
    )
    
    if cache:
        etag_key = ':'.join([feed_url, 'etag'])
        modified_key = ':'.join([feed_url, 'modified'])
        etag = cache.get(etag_key)
        modified = cache.get(modified_key)
    else:
        etag = None
        modified = None

    feed_response = feedparser.parse(feed_url, etag=etag, modified=modified)

    entries = feed_response['entries']

    filtered_entries = []
    for entry in entries:
        for f in filters:
            entry = f(entry)
            if not entry:
                break
        if entry:
            filtered_entries.append(entry)

    if filtered_entries:
        signal.send(
            'entries_created',
            id=feed_url,
            data=entries,
        )
        for a in aggregators:
            try:
                a.submit(filtered_entries)
            except AttributeError:
                pass

    if cache:
        cache[etag_key] = feed_response.get('etag')
        cache[modified_key] = feed_response.get('updated_parsed')  # 9-tuple
