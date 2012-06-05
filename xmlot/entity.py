from lxml import objectify
from xmlot.types import XmlRelation


class XmlEntity(object):
    xml_path = None # needs to be overridden
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
            elem = objectify.Element(self.xml_tag)
        self.__dict__['_elem'] = elem

    def __getattr__(self, attr):
        sqltype = getattr(self.types, attr, None)
        if isinstance(sqltype, XmlRelation):
            return sqltype.lookup(self, attr)
        else:
            val = getattr(self._elem, attr, None)
            if val is not None and sqltype is not None:
                val = sqltype.python_type(val)
        return val

    def __setattr__(self, attr, value):
        setattr(self._elem, attr, value)




def xmldump(root):
    from lxml import etree
    etree.strip_attributes(root, '{http://codespeak.net/lxml/objectify/pytype}pytype')
    etree.strip_attributes(root, '{http://www.w3.org/2001/XMLSchema-instance}nil')
    etree.cleanup_namespaces(root)
    print etree.tostring(root, pretty_print=True)
