from .dag import FilterNode, AccumulatorNode, SourceNode
from .util import entity_names_to_codepoints, always, never,\
        entry_guarantee_date
from six.moves.urllib.parse import urlparse
import feedparser
from feedgen.feed import FeedGenerator, FeedEntry
from lxml import etree

CDATA_MIMETYPES = {'text/html', 'text/xml', 'application/xhtml',
                   'application/xhtml+xml'}
FEEDGEN_LINK_PROPERTIES = {'title', 'hreflang', 'length', 'href',
                           'rel', 'type'}
FEEDGEN_REL_LINK_VALUES = {'alternate', 'enclosure', 'related', 'self', 'via'}


class FeedNode(SourceNode):
    def __init__(self, feed_url, options=None):
        try:
            parsed = urlparse(feed_url)
        except TypeError, AttributeError:
            raise TypeError('FeedNode requires a string-based URL')
        if not parsed.scheme or not parsed.netloc:
            raise ValueError('FeedNode requires a fully-qualified URL')

        super(FeedNode, self).__init__(feed_url, options)
        self.feed_url = feed_url

    def action(self):
        d = feedparser.parse(self.feed_url)
        result = None
        if d.entries:
            result = d.entries
        return result


class FeedGeneratorNode(AccumulatorNode):
    def __init__(self, name, options=None):
        if not options:
            options = {}
        if not options.get('output_file'):
            raise ValueError('output file is required')
        options['conditional_actions'] = [(always, self.generate_feed)]
        super(FeedGeneratorNode, self).__init__(name, options)
        fg = FeedGenerator()
        self.generator = fg
        self.filter_invalid = options.get('filter_invalid', False)
        self.output_file = options['output_file']
        self.entries = []

    def action(self, payload):
        returnable = []
        for entry in payload:
            fe = FeedEntry()
            valid = False
            fe.id(entry['id'])
            author_detail = entry.get('author_detail')
            if author_detail and 'href' in author_detail:
                author_detail['uri'] = author_detail['href']
                del author_detail['href']
            fe.author(author_detail)
            fe.updated(entry.get('updated'))
            fe.published(entry.get('published'))
            fe.contributor(entry.get('contributors'))
            category = entry.get('tags')
            if category == []:
                category = None
            fe.category(category)
            if entry.get('content'):
                # TODO: there's data loss here, as we may be losing secondary
                # content items from an Atom feed.
                # TODO: Handle "src" properly when generating feed
                content = entry['content'][0]
                value = content['value']
                t = content['type']
                if content['type'] == 'application/xhtml+xml':
                    t = 'xhtml'
                    value = entity_names_to_codepoints(value)
                fe.content(
                    content=value,
                    type=t
                )
            if entry.get('title_detail'):
                if entry['title_detail']['type'] in CDATA_MIMETYPES:
                    # Not currently accounting for "base"
                    fe.title(etree.CDATA(entry['title_detail']['value']))
                else:
                    fe.title(entry['title_detail']['value'])
            if fe.title() == '':
                fe.title('Untitled')
            elif entry.get('title'):
                fe.title(entry['title'])
            if entry.get('summary_detail'):
                if entry['summary_detail']['type'] in \
                            {'text/html', 'text/xhtml'}:
                    # Not currently accounting for "base"
                    fe.summary(etree.CDATA(entry['summary_detail']['value']))
                else:
                    fe.summary(entry['summary_detail']['value'])
            elif entry.get('summary'):
                fe.summary(entry['summary'])
            for link in entry.get('links', []):
                if link.get('rel') == 'alternate':
                    valid = True
                if link.get('rel') and link['rel'] not in\
                        FEEDGEN_REL_LINK_VALUES:
                    continue
                # A workaround required for feedgen at the moment -- for an
                # example in the wild of non-standard link properties, see
                # http://rc3.org/feed
                for prop in link.keys():
                    if prop not in FEEDGEN_LINK_PROPERTIES:
                        del(link[prop])
                fe.link(**link)
            if not valid and entry.get('link'):
                fe.link({
                    'rel': 'alternate',
                    'href': entry.get('link'),
                })
                valid = True
            if valid:
                returnable.append(entry)
                self.entries.append(fe)
            elif not self.filter_invalid:
                returnable.append(entry)
        return returnable

    def generate_feed(self):
        sorted_entries = sorted(self.entries, key=entry_guarantee_date)
        for fe in reversed(sorted_entries):
            self.generator.add_entry(fe)
        with open(self.output_file, 'w') as file:
            file.write(self.generator.atom_str(pretty=True).encode('utf-8'))
