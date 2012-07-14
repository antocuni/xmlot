from lxml import objectify
from xmlot.types import XmlRelation, Type

def new_element(tag, xmlns=None):
    if xmlns is not None:
        tag = '{%s}%s' % (xmlns, tag)
    return objectify.Element(tag)

class XmlEntity(object):
    xmlns = None   # default to no namespace
    xml_path = None # needs to be overridden
    xml_tag = None  # needs to be overridden
    class types:
        pass

    _cache = {}

    def __new__(cls, elem=None):
        if elem is not None and elem in cls._cache:
            return cls._cache[elem]
        obj = object.__new__(cls, elem)
        cls._cache[elem] = obj
        return obj

    def __init__(self, elem=None):
        if elem is None:
            elem = new_element(self.xml_tag, self.xmlns)
            if hasattr(self, 'types'):
                for subtag, xmltype in self.types.__dict__.iteritems():
                    if isinstance(xmltype, Type):
                        child = new_element(subtag, self.xmlns)
                        elem.append(child)
        assert isinstance(elem, objectify.ObjectifiedElement)
        self.__dict__['_elem'] = elem

    def __getattr__(self, attr):
        xmltype = getattr(self.types, attr, None)
        if xmltype:
            return xmltype.lookup(self, attr)
        else:
            return getattr(self._elem, attr, None)

    def __setattr__(self, attr, value):
        xmltype = getattr(self.types, attr, None)
        if xmltype:
            value = xmltype.toxml(value)
        return setattr(self._elem, attr, value)


def xmltostring(root):
    from lxml import etree
    etree.strip_attributes(root, '{http://codespeak.net/lxml/objectify/pytype}pytype')
    etree.strip_attributes(root, '{http://www.w3.org/2001/XMLSchema-instance}nil')
    etree.cleanup_namespaces(root)
    return etree.tostring(root, pretty_print=True)

def xmldump(root):
    print xmltostring(root)
