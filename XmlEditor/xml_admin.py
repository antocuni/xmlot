from camelot.admin.object_admin import ObjectAdmin
from camelot.view.proxy.collection_proxy import CollectionProxy
from camelot.view.model_thread import gui_function
from camelot.view.controls.tableview import TableView
from camelot.admin.action.application_action import OpenTableView
from camelot.admin.action.list_action import OpenFormView

def getattr_ex(obj, attrs):
    for attr in attrs.split('.'):
        obj = getattr(obj, attr)
    return obj


class XmlEntity(object):
    xml_path = None # needs to be overridden
    class types:
        pass

    def __init__(self, elem):
        self.__dict__['_elem'] = elem

    def __getattr__(self, attr):
        sqltype = getattr(self.types, attr, None)
        if isinstance(sqltype, XmlList):
            val = getattr_ex(self._elem, sqltype.subpath)
        else:
            val = getattr(self._elem, attr)
            if sqltype is not None:
                val = sqltype.python_type(val)
        return val

    def __setattr__(self, attr, value):
        setattr(self._elem, attr, value)


class XmlList(object):
    """
    Field type which represent a nested list of XML nodes
    """

    def __init__(self, subpath, entity_cls):
        self.subpath = subpath
        self.entity_cls = entity_cls


class XmlOpenTableView(OpenTableView):
    """
    It works exactly like a OpenTableView, but does not check that
    _entity_admin is effectively an EntityAdmin. It works well e.g. with
    XmlAdmin
    """

    def __init__(self, entity_admin):
        self._entity_admin = entity_admin


class XmlTableView(TableView):

    table_model = CollectionProxy

    def create_table_model(self, admin):
        xml_root = admin.app_admin.xml_root
        xml_path = admin.entity.xml_path
        entity_cls = admin.entity
        def get_entities():
            elem = getattr_ex(xml_root, xml_path)
            return map(entity_cls, elem)
        return self.table_model(admin,
                                get_entities,
                                admin.get_columns)


class XmlAdmin(ObjectAdmin):

    TableView = XmlTableView
    list_action = OpenFormView()
    search_all_fields = False
    list_search = []

    @gui_function
    def create_table_view(self, gui_context):
        return self.TableView(gui_context, self)

    def get_filters(self):
        return []

    def get_actions(self):
        return []

    def get_query(self):
        return 'QUERY' # XXX

    def get_field_attributes(self, field_name):
        from sqlalchemy.types import Unicode
        from camelot.view.field_attributes import _sqlalchemy_to_python_type_
        from camelot.view.controls import delegates
        #
        attrs = ObjectAdmin.get_field_attributes(self, field_name)
        sqltype = getattr(self.entity.types, field_name, Unicode())
        get_attrs = _sqlalchemy_to_python_type_.get(sqltype.__class__, None)
        if get_attrs:
            attrs.update(get_attrs(sqltype))
        elif isinstance(sqltype, XmlList):
            target = sqltype.entity_cls
            admin = target.Admin(self.app_admin, target)
            attrs.update(
                python_type = list,
                editable = True,
                nullable = True,
                delegate = delegates.One2ManyDelegate,
                target = target,
                create_inline = False,
                direction = 'onetomany',
                admin = admin,
                )

        return attrs
