import py
from lxml import objectify
from sqlalchemy.types import Boolean, Integer, Unicode
from XmlEditor.xml_admin import getattr_ex, XmlEntity, XmlList, XmlListWrapper

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
    assert f.non_existent is None

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
        xml_path = 'bars'
        xml_tag = 'bar'
    class Foo(XmlEntity):
        xml_path = ''
        xml_tag = 'foo'
        class types:
            bars = XmlList(Bar)
    #
    f = Foo(elem)
    bars = f.bars
    assert isinstance(bars, XmlListWrapper)
    assert isinstance(bars[0], XmlEntity)
    assert bars[0].x == 'hello'
    assert bars[1].x == 'world'
    newbar = Bar()
    newbar.x = 'foobar'
    bars.append(newbar)
    assert bars[2].x == 'foobar'
    assert f.bars[2].x == 'foobar'
    assert elem.bars.bar[2].x == 'foobar'
    #
    f = Foo()
    bars = f.bars
    assert isinstance(bars, XmlListWrapper)
    assert len(bars) == 0
