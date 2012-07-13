from datetime import datetime
from lxml import objectify
from sqlalchemy import types as sqltypes

class Type(object):
    def __init__(self, name=None):
        self.name = name

    def toxml(self, value):
        return value

    def matches(self, value, text):
        return False

class PrimitiveType(Type):
    sqltype = None
    python_type = staticmethod(lambda x: x)

    def lookup(self, obj, attr):
        val = getattr(obj._elem, attr, None)
        if val is not None:
            val = self.python_type(val)
        return val

    def matches(self, value, text):
        try:
            value2 = self.python_type(text)
        except ValueError:
            return False
        return value == value2

class Integer(PrimitiveType):
    sqltype = sqltypes.Integer()
    python_type = int


class Boolean(PrimitiveType):
    sqltype = sqltypes.Boolean()
    @staticmethod
    def python_type(val):
        if isinstance(val, basestring):
            val = val.strip().lower()
            return val == 'true'
        return bool(val) # ???

class Unicode(PrimitiveType):
    sqltype = sqltypes.Unicode()
    @staticmethod
    def python_type(x):
        return unicode(x.text)

    def matches(self, value, text):
        return text in unicode(value).lower()

class Float(PrimitiveType):
    sqltype = sqltypes.Float()
    python_type = float


class DateTime(PrimitiveType):
    sqltype = sqltypes.DateTime()
    default_format = '%Y-%m-%d %H:%M:%S'

    def __init__(self, name=None, format=None):
        PrimitiveType.__init__(self, name)
        if format is None:
            format = self.default_format
        self.format = format
        
    def python_type(self, s):
        return datetime.strptime(unicode(s), self.format)

    def toxml(self, s):
        return s.strftime(self.format)

class XmlRelation(Type):
    pass

class XmlList(XmlRelation):
    """
    Field type which represent a nested list of XML nodes
    """

    def __init__(self, name, entity_cls):
        self.name = name
        self.subpath = entity_cls.xml_path
        self.entity_cls = entity_cls

    def lookup(self, obj, attr):
        try:
            subroot = getattr_ex(obj._elem, self.subpath)
        except AttributeError:
            assert '.' not in self.subpath, 'XXX implement me'
            subroot = objectify.Element(self.subpath)
            obj._elem.append(subroot)
        #
        try:
            val = getattr(subroot, self.entity_cls.xml_tag)
        except AttributeError:
            val = []
        return XmlListWrapper(subroot, self.entity_cls, val)


class XmlOneToMany(XmlRelation):

    def __init__(self, name, entity_cls, primary_key, foreign_key):
        self.name = name
        self.entity_cls = entity_cls
        self.primary_key = primary_key
        self.foreign_key = foreign_key

    def lookup(self, obj, attr):
        root = obj._elem.getroottree().getroot()
        subroot = getattr_ex(root, self.entity_cls.xml_path)
        elems = getattr(subroot, self.entity_cls.xml_tag)
        filtered_elems = []
        pkey_value = getattr(obj, self.primary_key)
        for elem in elems:
            if getattr(elem, self.foreign_key) == pkey_value:
                filtered_elems.append(elem)
        field_values = {self.foreign_key: pkey_value}
        return XmlOneToManyListWrapper(subroot, self.entity_cls,
                                       filtered_elems, field_values)


class XmlListWrapper(object):

    def __init__(self, root, Entity, items):
        self.root = root
        self.Entity = Entity
        self.items = items

    def append(self, obj):
        self.root.append(obj._elem)

    def __getitem__(self, i):
        return self.Entity(self.items[i])

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        for elem in self.items:
            yield self.Entity(elem)

    def filter(self, search_fields, text):
        text = text.lower()
        newitems = []
        for item in self:
            for field in search_fields:
                field_type = getattr(item.__class__.types, field, Unicode())
                field_val = getattr(item, field)
                if field_type.matches(field_val, text):
                    newitems.append(item)
        return self.__class__(self.root, self.Entity, newitems)


class XmlOneToManyListWrapper(XmlListWrapper):

    def __init__(self, root, Entity, items, field_values):
        XmlListWrapper.__init__(self, root, Entity, items)
        self.field_values = field_values

    def append(self, obj):
        for name, value in self.field_values.iteritems():
            setattr(obj, name, value)
        XmlListWrapper.append(self, obj)


def getattr_ex(obj, attrs):
    if attrs == '':
        return obj
    for attr in attrs.split('.'):
        obj = getattr(obj, attr)
    return obj


