import pyatom
import datetime
import json
import importlib

FILTER_MODULES = ['centaur.filters']
AGGREGATOR_MODULES = ['centaur.aggregators']


def kwargs_required(*argnames):
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            for name in argnames:
                if not isinstance(name, basestring):
                    next
                if name not in kwargs:
                    raise KeyError(
                        '{0} requires the following arguments: {1}'.
                        format(f.func_name, ', '.join(argnames))
                    )
            return f(*args, **kwargs)
        return wrapped_f
    return wrap

# In-memory caching to avoid our importlib dances when possible
_filter_cache = {}
_aggregator_cache = {}


def inflate_filter(filter_identifier, settings=None, filter_modules=None):
    """
    Transform a string (identifying a factory function) and a settings
    dictionary into a filter function. Accepts an optional list of module
    objects where filter functions may be found.
    """
    if not filter_modules:
        filter_modules = FILTER_MODULES
    if not settings:
        settings = {}
    f = None
    if filter_identifier in _filter_cache:
        # Is it in cache? Great.
        f = _filter_cache[filter_identifier]
    else:
        # Assume it's a fully-qualified name, mymodule.submodule.method
        pieces = filter_identifier.split(".")
        module_name = '.'.join(pieces[0:-1])
        if module_name:
            try:
                imported = importlib.import_module(module_name)
                f = getattr(imported, pieces[-1])
            except (ImportError, AttributeError) as e:
                pass
    if not f:
        # Last chance -- import everything in filter_modules
        # and check there.
        for module_name in filter_modules:
            try:
                imported = importlib.import_module(module_name)
                f = getattr(imported, filter_identifier)
            except (ImportError, AttributeError):
                pass
            if f:
                break
    if not f:
        raise ValueError('Unable to locate filter {0}'.
                         format(filter_identifier))
    _filter_cache[filter_identifier] = f
    inflated_function = f(**settings)
    return inflated_function


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
