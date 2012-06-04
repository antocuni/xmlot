import py
from lxml import objectify
from sqlalchemy.types import Boolean, Integer
from XmlEditor.xml_admin import getattr_ex, XmlEntity, XmlList

def test_getattr_ex():
    class A:
        class B:
            C = 42
    assert getattr_ex(A, 'B') is A.B
    assert getattr_ex(A, 'B.C') == 42
    with py.test.raises(AttributeError):
        getattr_ex(A, 'B.X')


def test_XmlEntity():
    elem = objectify.fromstring("<foo><x>hello</x></foo>")
    class Foo(XmlEntity):
        pass
    f = Foo(elem)
    assert f.x == 'hello'
    f.x = 'world'
    assert elem.x == 'world'

def test_XmlEntity_types():
    elem = objectify.fromstring("<foo><x>42</x></foo>")
    class Foo(XmlEntity):
        class types:
            x = Integer()
    f = Foo(elem)
    assert f.x == 42
    assert f.x.__class__ is int


def test_XmlEntity_list():
    elem = objectify.fromstring("""
        <foo>
          <bars>
            <bar><x>hello</x></bar>
            <bar><x>world</x></bar>
          </bars>
        </foo>
    """)
    class Bar(XmlEntity):
        pass
    class Foo(XmlEntity):
        class types:
            bars = XmlList('bars.bar', Bar)
    #
    f = Foo(elem)
    bars = f.bars
    assert iter(bars) # it's not a python list, but it's still iterable
    assert bars[0].x == 'hello'
    assert bars[1].x == 'world'

