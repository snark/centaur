from centaur import (util)
import types


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
