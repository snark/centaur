from nose.tools import raises
import unittest
from centaur import dag
from centaur.dag import Graph, FilterNode, SourceNode, AccumulatorNode
import codecs


# Some simple DAG classes for setting up a toy graph
class NameSource(SourceNode):
    def action(self):
        result = self.name
        return result


class Rot13Filter(FilterNode):
    def action(self, payload):
        return codecs.encode(payload, 'rot_13')


class ReverseFilter(FilterNode):
    def action(self, payload):
        return payload[::-1]


class SetAccumulator(AccumulatorNode):
    def __init__(self, name):
        def gathered_condition(self):
            return len(self.values) > 0

        def gathered_action(self):
            self.gathered = set(self.values)

        def ungathered_condition(self):
            return len(self.values) == 0

        def ungathered_action(self):
            return False

        options = {
            'conditional_actions': [
                (gathered_condition, gathered_action),
                (ungathered_condition, ungathered_action)
            ]
        }
        super(SetAccumulator, self).__init__(name, options)
        self.values = []
        self.gathered = set()

    def action(self, payload):
        self.values.append(payload)


class DAGGraphTest(unittest.TestCase):

    def setUp(self):
        self.s1 = SourceNode('s1')
        self.s2 = SourceNode('s1')
        self.f1 = FilterNode('f1')
        self.f2 = FilterNode('f2')
        self.f3 = FilterNode('f2')
        self.a1 = AccumulatorNode('a1')
        self.a2 = AccumulatorNode('a1')

    def testInstantiateAndConnect(self):
        graph = Graph()
        self.assertTrue(graph, 'Graph instantiates successfully')
        self.assertEquals(len(graph.nodes), 0, 'Graph starts empty')
        self.assertEquals(len(graph.sources), 0, 'Graph starts empty')
        self.assertEquals(len(graph.accumulators), 0, 'Graph starts empty')
        graph.connect(self.s1, self.f1)
        graph.connect(self.s1, self.f2)
        graph.connect(self.f1, self.a1)
        graph.connect(self.f2, self.a1)
        for n in [self.s1, self.f1, self.f2, self.a1]:
            self.assertTrue(n in graph.nodes)
        for n in [self.s2, self.f3, self.a2]:
            self.assertFalse(n in graph.nodes)
        self.assertTrue(self.s1 in graph.sources)
        self.assertTrue(self.a1 in graph.accumulators)
        self.assertTrue(self.f1 in self.s1.children)
        self.assertTrue(self.f2 in self.s1.children)
        self.assertTrue(self.a1 in self.f1.children)
        self.assertFalse(self.a1 in self.s1.children)

    @raises(ValueError)
    def testConnectNonNode(self):
        graph = Graph()
        graph.connect(self.s1, {})

    @raises(ValueError)
    def testSourceNodeChild(self):
        graph = Graph()
        graph.connect(self.a1, self.s1)

    def testAccumulatorConditionalActions(self):
        graph = Graph()
        foo = NameSource('foo')
        bar = NameSource('bar')
        rev1 = ReverseFilter('r1')
        acc = SetAccumulator('acc')

        graph.connect(rev1, acc)
        graph.connect(foo, rev1)
        graph.connect(bar, rev1)

        acc.check_conditions()
        # First conditional
        self.assertFalse(acc.gathered)
        graph.run_sources()
        graph.check_conditions()
        # Second conditional
        self.assertTrue('oof' in acc.gathered)
        self.assertTrue('rab' in acc.gathered)

    def testMultipleNodeChildren(self):
        graph = Graph()
        foo = NameSource('foo')
        rot13 = Rot13Filter('rot13')
        rev1 = ReverseFilter('r1')
        acc = SetAccumulator('acc')

        graph.connect(foo, rot13)
        graph.connect(rot13, acc)
        graph.connect(foo, rev1)
        graph.connect(rev1, acc)

        graph.run_sources()
        graph.check_conditions()
        self.assertTrue('oof' in acc.gathered)
        self.assertTrue('sbb' in acc.gathered)

    def testFilterChaining(self):
        graph = Graph()
        foo = NameSource('foo')
        rot13 = Rot13Filter('rot13')
        rev1 = ReverseFilter('r1')
        acc = SetAccumulator('acc')

        graph.connect(foo, rot13)
        graph.connect(rot13, rev1)
        graph.connect(rev1, acc)

        graph.run_sources()
        graph.check_conditions()
        self.assertTrue('bbs' in acc.gathered)
