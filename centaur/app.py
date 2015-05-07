import seria
from centaur.graph import Graph
from centaur.node import FeedNode, FeedGeneratorNode

def parse_config(f):
    # f is a file
    retval = None
    try:
        retval = seria.load(f).serialized
    except seria.serializers.Error:
        retval = False
    return retval

def build_graph(config):
    # config is an OrderedDict
    g = Graph()
    if not 'output_file' in config:
        raise ValueError('output file must be defined')
    out = FeedGeneratorNode('out', {'output_file': config['output_file']})
    for feed in config['feeds']:
        f = FeedNode(feed)
        g.connect(f, out)
    return g

def run_graph(g):
    g.run_sources()
    g.check_conditions()
