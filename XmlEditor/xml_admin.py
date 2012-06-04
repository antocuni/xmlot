from camelot.admin.object_admin import ObjectAdmin
from camelot.view.proxy.collection_proxy import CollectionProxy
from camelot.view.model_thread import gui_function
from camelot.view.controls.tableview import TableView
from camelot.admin.action.application_action import OpenTableView
from camelot.admin.action.list_action import OpenFormView

class XmlEntity(object):
    xml_path = None # needs to be overridden
    class types:
        pass

    def __init__(self, elem):
        self.__dict__['_elem'] = elem

    def __getattr__(self, attr):
        val = getattr(self._elem, attr)
        sqltype = getattr(self.types, attr, None)
        if sqltype is not None:
            val = sqltype.python_type(val)
        return val

    def __setattr__(self, attr, value):
        setattr(self._elem, attr, value)



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
            elem = xml_root
            for attr in xml_path.split('.'):
                elem = getattr(elem, attr)
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
        #
        attrs = ObjectAdmin.get_field_attributes(self, field_name)
        sqltype = getattr(self.entity.types, field_name, Unicode())
        get_attrs = _sqlalchemy_to_python_type_.get(sqltype.__class__, None)
        if get_attrs:
            attrs.update(get_attrs(sqltype))
        return attrs
