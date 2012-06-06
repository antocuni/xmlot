from lxml import objectify
from xmlot.types import XmlRelation


class XmlEntity(object):
    xml_ns = None   # default to no namespace
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
            tag = self.xml_tag
            if self.xml_ns is not None:
                tag = '{%s}%s' % (self.xml_ns, tag)
            elem = objectify.Element(tag)
        self.__dict__['_elem'] = elem

    def __getattr__(self, attr):
        xmltype = getattr(self.types, attr, None)
        if xmltype:
            return xmltype.lookup(self, attr)
        else:
            return getattr(self._elem, attr, None)

    def __setattr__(self, attr, value):
        setattr(self._elem, attr, value)




def xmldump(root):
    from lxml import etree
    etree.strip_attributes(root, '{http://codespeak.net/lxml/objectify/pytype}pytype')
    etree.strip_attributes(root, '{http://www.w3.org/2001/XMLSchema-instance}nil')
    etree.cleanup_namespaces(root)
    print etree.tostring(root, pretty_print=True)
