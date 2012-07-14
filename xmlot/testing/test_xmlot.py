import py
from datetime import datetime
from lxml import objectify
from xmlot.entity import XmlEntity, xmldump
from xmlot.types import (getattr_ex, XmlList, XmlListWrapper, XmlOneToMany,
                         XmlOneToManyListWrapper, Boolean, Integer, Unicode, DateTime)

def test_getattr_ex():
    class A:
        class B:
            C = 42
    assert getattr_ex(A, 'B') is A.B
    assert getattr_ex(A, 'B.C') == 42
    assert getattr_ex(A, '') is A
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

def test_XmlEntity_default_children():
    class Foo(XmlEntity):
        xmlns = 'http://foo.bar'
        xml_tag = 'foo'
        class types:
            name = Unicode('name of foo')
    f = Foo()
    children = f._elem.getchildren()
    assert f.name == ''
    assert len(children) == 1
    assert children[0].tag == '{http://foo.bar}name'


def test_XmlEntity_namespace():
    class Foo(XmlEntity):
        xml_tag = 'foo'
    class Bar(XmlEntity):
        xmlns = 'http://bar.com'
        xml_tag = 'bar'
    f = Foo()
    assert f._elem.tag == 'foo'
    b = Bar()
    assert b._elem.tag == '{http://bar.com}bar'

def test_Boolean():
    assert Boolean.python_type('true') == True
    assert Boolean.python_type('false') == False

def test_Boolean_match():
    b = Boolean('foo')
    assert b.matches(True, 'true')
    assert b.matches(False, 'false')
    assert not b.matches(True, 'hello')
    assert not b.matches(False, 'hello')

def test_XmlEntity_types():
    elem = objectify.fromstring("<foo><x>42</x> <y>2012-05-13</y></foo>")
    class Foo(XmlEntity):
        class types:
            x = Integer()
            y = DateTime(format='%Y-%m-%d')
    f = Foo(elem)
    assert f.x == 42
    assert f.x.__class__ is int
    #
    assert f.y == datetime(2012, 5, 13)
    assert f.y.__class__ is datetime

def test_XmlEntity_cache():
    elem = objectify.fromstring("<foo><x>hello</x></foo>")
    class Foo(XmlEntity):
        pass
    f1 = Foo(elem)
    f2 = Foo(elem)
    assert f1 is f2

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
            bars = XmlList('bars', Bar)
    #
    f = Foo(elem)
    bars = f.bars
    assert isinstance(bars, XmlListWrapper)
    assert isinstance(bars[0], Bar)
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
    assert bars.root.tag == 'bars'
    assert bars.root.getparent() is f._elem


def test_XmlEntity_list_namespace():
    class Bar(XmlEntity):
        xmlns = 'http://foo.bar'
        xml_path = 'bars'
        xml_tag = 'bar'
    class Foo(XmlEntity):
        xmlns = 'http://foo.bar'
        xml_path = ''
        xml_tag = 'foo'
        class types:
            bars = XmlList('bars', Bar)
    #
    f = Foo()
    bars = f.bars
    assert isinstance(bars, XmlListWrapper)
    mybar = Bar()
    bars.append(mybar)
    assert f.bars[0]._elem is mybar._elem



def test_XmlList_filter():
    root = objectify.fromstring("""
      <bars>
        <bar>
          <x>hello</x>
          <y>world</y>
          <z>42</z>
          <fruit>apple</fruit>
        </bar>
        <bar>
          <x>foo</x>
          <y>bar</y>
          <z>1042</z>
          <fruit>orange</fruit>
        </bar>
      </bars>
    """)
    class Bar(XmlEntity):
        xml_path = ''
        xml_tag = 'bar'
        class types:
            z = Integer()
        class Admin:
            field_attributes = {
                'fruit': {
                    'choices': lambda obj: [('apple', 'mela'),
                                            ('orange', 'arancia')]
                    }
                }

    mylist = XmlListWrapper(root, Bar, root.bar)
    mylist2 = mylist.filter(['x'], 'hel')
    assert len(mylist2) == 1
    assert mylist2[0].x == 'hello'
    #
    mylist2 = mylist.filter(['x', 'y'], 'ba')
    assert len(mylist2) == 1
    assert mylist2[0].x == 'foo'
    #
    mylist2 = mylist.filter([], '')
    assert len(mylist2) == 0
    #
    mylist2 = mylist.filter(['x'], 'hello xxx')
    assert len(mylist2) == 0
    #
    mylist2 = mylist.filter(['z'], '42')
    assert len(mylist2) == 1
    #
    mylist2 = mylist.filter(['fruit'], 'app')
    assert len(mylist2) == 0
    #
    mylist2 = mylist.filter(['fruit'], 'me')
    assert len(mylist2) == 1
    assert mylist2[0].fruit == 'apple'



def test_XmlOneToMany():
    root = objectify.fromstring("""
        <root>
          <Persons>
             <Person>
               <name>alice</name>
             </Person>
             <Person>
               <name>bob</name>
             </Person>
          </Persons>
          <Jobs>
             <Job>
               <title>foo</title>
               <person>alice</person>
             </Job>
             <Job>
               <title>bar</title>
               <person>alice</person>
             </Job>
             <Job>
               <title>foobar</title>
               <person>bob</person>
             </Job>
          </Jobs>
        </root>
    """)
    class Job(XmlEntity):
        xml_path = 'Jobs'
        xml_tag = 'Job'
    class Person(XmlEntity):
        class types:
            jobs = XmlOneToMany('jobs', Job, primary_key='name', foreign_key='person')
    #
    alice = Person(root.Persons.Person[0])
    bob = Person(root.Persons.Person[1])
    a_jobs = alice.jobs
    assert isinstance(a_jobs, XmlOneToManyListWrapper)
    assert len(a_jobs) == 2
    assert a_jobs[0].title == 'foo'
    assert a_jobs[1].title == 'bar'
    #
    b_jobs = bob.jobs
    assert len(b_jobs) == 1
    assert b_jobs[0].title == 'foobar'
    #
    myjob = Job()
    myjob.title = 'xxx'
    assert myjob.person is None
    b_jobs.append(myjob)
    assert myjob.person == 'bob'
    assert root.Jobs.Job[3].title == 'xxx'
    assert root.Jobs.Job[3].person == 'bob'
