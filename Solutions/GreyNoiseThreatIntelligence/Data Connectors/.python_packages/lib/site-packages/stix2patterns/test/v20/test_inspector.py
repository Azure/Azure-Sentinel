import pytest

from stix2patterns.inspector import INDEX_STAR
from stix2patterns.v20.pattern import Pattern


@pytest.mark.parametrize(u"pattern,expected_qualifiers", [
    (u"[foo:bar = 1]", set()),
    (u"[foo:bar = 1] REPEATS 5 TIMES", set([u"REPEATS 5 TIMES"])),
    (u"[foo:bar = 1] WITHIN 10.3 SECONDS", set([u"WITHIN 10.3 SECONDS"])),
    (u"[foo:bar = 1] WITHIN 123 SECONDS", set([u"WITHIN 123 SECONDS"])),
    (u"[foo:bar = 1] START '1932-11-12T15:42:15Z' STOP '1964-10-53T21:12:26Z'",
        set([u"START '1932-11-12T15:42:15Z' STOP '1964-10-53T21:12:26Z'"])),
    (u"[foo:bar = 1] REPEATS 1 TIMES REPEATS 2 TIMES",
        set([u"REPEATS 1 TIMES", u"REPEATS 2 TIMES"])),
    (u"[foo:bar = 1] REPEATS 1 TIMES AND [foo:baz = 2] WITHIN 1.23 SECONDS",
        set([u"REPEATS 1 TIMES", u"WITHIN 1.23 SECONDS"])),
    (u"([foo:bar = 1] START '1932-11-12T15:42:15Z' STOP '1964-10-53T21:12:26Z' AND [foo:abc < h'12ab']) WITHIN 22 SECONDS "
     u"OR [frob:baz NOT IN (1,2,3)] REPEATS 31 TIMES",
        set([u"START '1932-11-12T15:42:15Z' STOP '1964-10-53T21:12:26Z'",
            u"WITHIN 22 SECONDS", u"REPEATS 31 TIMES"]))
])
def test_qualifiers(pattern, expected_qualifiers):
    compiled_pattern = Pattern(pattern)
    pattern_data = compiled_pattern.inspect()

    assert pattern_data.qualifiers == expected_qualifiers


@pytest.mark.parametrize(u"pattern,expected_obs_ops", [
    (u"[foo:bar = 1]", set()),
    (u"[foo:bar = 1] AND [foo:baz > 25.2]", set([u"AND"])),
    (u"[foo:bar = 1] OR [foo:baz != 'hello']", set([u"OR"])),
    (u"[foo:bar = 1] FOLLOWEDBY [foo:baz IN (1,2,3)]", set([u"FOLLOWEDBY"])),
    (u"[foo:bar = 1] AND [foo:baz = 22] OR [foo:abc = '123']", set([u"AND", u"OR"])),
    (u"[foo:bar = 1] OR ([foo:baz = false] FOLLOWEDBY [frob:abc LIKE '123']) WITHIN 46.1 SECONDS",
        set([u"OR", u"FOLLOWEDBY"]))
])
def test_observation_ops(pattern, expected_obs_ops):
    compiled_pattern = Pattern(pattern)
    pattern_data = compiled_pattern.inspect()

    assert pattern_data.observation_ops == expected_obs_ops


@pytest.mark.parametrize(u"pattern,expected_comparisons", [
    (u"[foo:bar = 1]", {u"foo": [([u"bar"], u"=", u"1")]}),
    (u"[foo:bar=1 AND foo:baz=2]", {u"foo": [([u"bar"], u"=", u"1"), ([u"baz"], u"=", u"2")]}),
    (u"[foo:bar NOT !=1 OR bar:foo<12.3]", {
        u"foo": [([u"bar"], u"NOT !=", u"1")],
        u"bar": [([u"foo"], u"<", u"12.3")]
    }),
    (u"[foo:bar=1] OR [foo:baz MATCHES '123\\\\d+']", {
        u"foo": [([u"bar"], u"=", u"1"), ([u"baz"], u"MATCHES", u"'123\\\\d+'")]
    }),
    (u"[foo:bar=1 AND bar:foo NOT >33] REPEATS 12 TIMES OR "
     u"  ([baz:bar ISSUBSET '1234'] FOLLOWEDBY [baz:quux NOT LIKE 'a_cd'])",
     {
         u"foo": [([u"bar"], u"=", u"1")],
         u"bar": [([u"foo"], u"NOT >", u"33")],
         u"baz": [([u"bar"], u"ISSUBSET", u"'1234'"), ([u"quux"], u"NOT LIKE", u"'a_cd'")]
     }),
    (u"[obj-type:a.b[*][1].'c-d' NOT ISSUPERSET '1.2.3.4/16']", {
        u"obj-type": [([u"a", u"b", INDEX_STAR, 1, u"c-d"], u"NOT ISSUPERSET", u"'1.2.3.4/16'")]
    }),
])
def test_comparisons(pattern, expected_comparisons):
    compiled_pattern = Pattern(pattern)
    pattern_data = compiled_pattern.inspect()

    assert pattern_data.comparisons == expected_comparisons
