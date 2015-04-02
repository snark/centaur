class Graph(object):
    def __init__(self):
        self.nodes = set()
        self.sources = set()
        self.accumulators = set()

    def add_node(self, node):
        if not isinstance(node, Node):
            raise ValueError('Cannot add non-Node to graph')
        if isinstance(node, SourceNode):
            self.sources.add(node)
        if isinstance(node, AccumulatorNode):
            self.accumulators.add(node)
        self.nodes.add(node)

    def run_sources(self):
        for source in self.sources:
            source.run()

    def check_conditions(self):
        for accumulator in self.accumulators:
            accumulator.check_conditions()

    def connect(self, from_node, to_node):
        self.add_node(from_node)
        self.add_node(to_node)
        from_node.add_child(to_node)

class Node(object):
    def __init__(self, name, options=None):
        self.name = name
        if not options:
            options = {}
        self.options = options
        self.children = set()
        self.parents = set()

    def run(self, payload=None):
        output = self.action(payload)
        if output is not None:
            for child in self.children:
                child.run(output)

    def action(self):
        return None

    def _is_source(self):
        return False

    is_source = property(_is_source)

    def is_accumulator(self):
        return False

    def add_child(self, child_node):
        if not isinstance(child_node, Node):
            raise ValueError("Cannot connect non-Node")
        if isinstance(child_node, SourceNode):
            raise ValueError("SourceNode cannot be a child")
        if child_node in self.ancestors():
            raise ValueError("Cannot create graph cycle")
        child_node.parents.add(self)
        self.children.add(child_node)

    def ancestors(self):
        ancestors = set()
        unvisited_ancestors = self.parents.copy()
        visited_ancestors = set()
        while len(unvisited_ancestors):
            ancestor = unvisited_ancestors.pop()
            if ancestor not in visited_ancestors:
                unvisited_ancestors = unvisited_ancestors.union(ancestor.parents)
                visited_ancestors.add(ancestor)
        return visited_ancestors

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Node: {}".format(self.name)

class SourceNode(Node):
    def run(self):
        output = self.action()
        if output is not None:
            for child in self.children:
                child.run(output)

    def _is_source(self):
        return True

class FilterNode(Node):
    pass

class AccumulatorNode(Node):
    def __init__(self, name, options=None):
        super(AccumulatorNode, self).__init__(name, options)
        self.conditions = []
        if options and options.get('conditional_actions'):
            try:
                for conditional_tuple in options['conditional_actions']:
                    if not isinstance(conditional_tuple, tuple):
                        raise ValueError(
                            'conditional items must be (condition, action)'
                            ' tuples'
                        )
                    c, a = conditional_tuple
                    if not callable(c):
                        raise ValueError(
                            'conditional action conditions must be callable'
                        )
                    if not callable(a):
                        raise ValueError(
                            'conditional action actions must be callable'
                        )
                    self.conditions.append(conditional_tuple)
            except TypeError:
                raise ValueError(
                    'conditional_actions argument must be iterable'
                )


    def check_conditions(self):
        for (condition, action) in self.conditions:
            # Some unwinding to make sure we're not passing self into
            # a bound method as an argument
            condition_is_bound = False
            action_is_bound = False
            try:
                condition_is_bound = condition.__self__ == self
            except AttributeError:
                pass
            try:
                action_is_bound = action.__self__ == self
            except AttributeError:
                pass
            check = None
            if condition_is_bound:
                check = condition()
            else:
                check = condition(self)
            if check and action_is_bound:
                action()
            elif check:
                action(self)
