from sqlalchemy import types as sqltypes

class Type(object):
    def __init__(self, name=None):
        self.name = name


class PrimitiveType(Type):
    sqltype = None

    def lookup(self, obj, attr):
        val = getattr(obj._elem, attr, None)
        if val is not None:
            val = self.sqltype.python_type(val)
        return val

class Integer(PrimitiveType):
    sqltype = sqltypes.Integer()

class Boolean(PrimitiveType):
    sqltype = sqltypes.Boolean()

class Unicode(PrimitiveType):
    sqltype = sqltypes.Unicode()


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
            val = getattr(subroot, self.entity_cls.xml_tag)
        except AttributeError:
            subroot = obj._elem # ???
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


class XmlListWrapper(list):

    def __init__(self, root, Entity, items):
        items = map(Entity, items)
        list.__init__(self, items)
        self.root = root

    def append(self, obj):
        list.append(self, obj)
        self.root.append(obj._elem)

class XmlOneToManyListWrapper(XmlListWrapper):

    def __init__(self, root, Entity, items, field_values):
        XmlListWrapper.__init__(self, root, Entity, items)
        self.field_values = field_values

    def append(self, obj):
        for name, value in self.field_values.iteritems():
            setattr(obj, name, value)
        XmlListWrapper.append(self, obj)


def getattr_ex(obj, attrs):
    for attr in attrs.split('.'):
        obj = getattr(obj, attr)
    return obj


