from .util import (generate_feed, validate_feed_settings)
import io
import os.path
from jinja2 import (Environment, FileSystemLoader)


def atom_simple(filename=None, max_results=10, feed_settings=None):
    """
    An aggregator that stores sent entries in an internal list and,
    on GeneratorExit, generates an Atom feed contaning those entries.
    """
    # we do this check 'cause we may get passed a list of keyword args
    # and can't guarantee order
    # so we can't make filename a required arg at the interpreter level
    if not filename:
        raise TypeError('atom_simple() requires filename argument')
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
        if max_results:
            entries = entries[0:max_results]
        new_feed = generate_feed(entries, settings=feed_settings)
        with io.open(filename, mode='w', encoding='utf-8') as f:
            f.write(new_feed.to_string())


def template_simple(
        template_filename=None,
        output_filename=None,
        max_results=10,
        output_settings=None,
    ):
    if not template_filename:
        raise TypeError(
                'template_simple() requires template_filename argument'
            )
    if not output_filename:
        raise TypeError(
                'template_simple() requires output_filename argument'
            )
    if not os.path.isfile(template_filename):
        raise ValueError('{} does not exist'.format(template_filename))
    template_dir, template_name = os.path.split(template_filename)
    try:
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_name)
    except Exception as e:
        # TODO - Better handling here
        raise
    entries = []
    try:
        while True:
            entry, context = yield
            entries.append(entry)
    except GeneratorExit:
        entries.sort(reverse=True,
                     key=lambda e:
                     e.get('updated_parsed', e.get('created_parsed')))
        if max_results:
            entries = entries[0:max_results]
        for e in entries:
            # TODO: Make this behavior more robust and split it out
            # into a utlity function
            e['content_reconstituted'] = e['content'][0]['value']
        out = template.render(settings=output_settings, entries=entries)
        with io.open(output_filename, mode='w', encoding='utf-8') as f:
            f.write(out)
