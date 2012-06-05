from camelot.view.proxy.collection_proxy import CollectionProxy
from camelot.view.controls.tableview import TableView
from camelot.admin.action.application_action import OpenTableView
from xmlot.types import getattr_ex, XmlListWrapper


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
            subroot = getattr_ex(xml_root, xml_path)
            items = getattr(subroot, entity_cls.xml_tag)
            return XmlListWrapper(subroot, admin.entity, items)
        return self.table_model(admin,
                                get_entities,
                                admin.get_columns)
