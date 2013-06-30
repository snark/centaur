from centaur import (util)
import types

def pass_filter(**kwargs):
    def filter(entry):
        return entry
    return filter

def fail_filter(**kwargs):
    def filter(entry):
        return False
    return filter

e1 = {"title": "foo bar"}
e2 = {"title": "bar baz"}
e3 = {"title": "baz zap"}
metasyntactic_feed = [e1, e2, e3]

def test_any_of_inflation():
    util.FILTER_MODULES.append(__name__)
    # Pass in a dict argument
    dict_based_filter = util.inflate_filter(
        'any_of',
        {
            'filters': [
                {'title_matches': {'strings': ['baz']}}
            ]
        }
    )
    filtered_entries = []
    for entry in metasyntactic_feed:
        entry = dict_based_filter(entry)
        if entry:
            filtered_entries.append(entry)
    assert filtered_entries == [e2, e3]
    # Or strings
    string_based_filter = util.inflate_filter(
        'any_of',
        {
            'filters': [
                'pass_filter',
                'fail_filter'
            ]
        }
    )
    filtered_entries = []
    for entry in metasyntactic_feed:
        entry = string_based_filter(entry)
        if entry:
            filtered_entries.append(entry)
    assert filtered_entries == [e1, e2, e3]
    # Or fully-inflated filters
    pass_f = util.inflate_filter(
        'pass_filter',
        None
    )
    fail_f = util.inflate_filter(
        'pass_filter',
        None
    )
    func_based_filter = util.inflate_filter(
        'any_of',
        {
            'filters': [
                pass_f,
                fail_f,
            ]
        }
    )
    filtered_entries = []
    for entry in metasyntactic_feed:
        entry = func_based_filter(entry)
        if entry:
            filtered_entries.append(entry)
    assert filtered_entries == [e1, e2, e3]

def test_any_of_behavior():
    multi_match = util.inflate_filter(
        'any_of',
        {
            'filters': [
                {'title_matches': {'strings': ['bar']}},
                {'title_matches': {'strings': ['baz']}}
            ]
        }
    )
    filtered_entries = []
    for entry in metasyntactic_feed:
        entry = multi_match(entry)
        if entry:
            filtered_entries.append(entry)
    assert filtered_entries == [e1, e2, e3]
    one_failure = util.inflate_filter(
        'any_of',
        {
            'filters': [
                {'title_matches': {'strings': ['quux']}},
                {'title_matches': {'strings': ['baz']}}
            ]
        }
    )
    filtered_entries = []
    for entry in metasyntactic_feed:
        entry = one_failure(entry)
        if entry:
            filtered_entries.append(entry)
    assert filtered_entries == [e2, e3]
    only_failure = util.inflate_filter(
        'any_of',
        {
            'filters': [
                {'title_matches': {'strings': ['quux']}}
            ]
        }
    )
    filtered_entries = []
    for entry in metasyntactic_feed:
        entry = only_failure(entry)
        if entry:
            filtered_entries.append(entry)
    assert filtered_entries == []

def test_inflation():
    passable = {"title": "fooby"}
    failable = {"title": "baz zap"}
    # Inflate with just a function name from the centaur.filters module
    util._filter_cache = {}
    f1 = util.inflate_filter(
        'title_matches',
        {'strings': ['foo', 'bar']}
    )
    assert isinstance(f1, types.FunctionType),\
        'function-name style import does not return a function'
    assert f1(passable) == passable,\
        'fully-qualified import returns bad function'
    assert not f1(failable),\
        'fully-qualified import returns bad function'
    # Inflate with a fully-qualified module.function-style string
    f2 = util.inflate_filter(
        'centaur.filters.title_matches',
        {'strings': ['foo', 'bar']}
    )
    assert isinstance(f2, types.FunctionType),\
        'fully-qualified import does not return a function'
    assert f2(passable) == passable,\
        'fully-qualified import returns bad function'
    assert not f2(failable),\
        'fully-qualified import returns bad function'

    def dummy(entry):
        return 'xyzzy'

    def dummy_factory(**kwargs):
        return dummy

    util._filter_cache['title_matches'] = dummy_factory
    f3 = util.inflate_filter(
        'title_matches',
        {'strings': ['foo', 'bar']}
    )
    assert f3(passable) == 'xyzzy',\
        'inflate_filter does not preferentially use cached values'
