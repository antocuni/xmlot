from PyQt4 import QtCore
from camelot.view.proxy.collection_proxy import CollectionProxy
from camelot.view.controls.tableview import TableView
from camelot.admin.action.application_action import OpenTableView

class XmlCollectionProxy(CollectionProxy):

    _query_getter = None

    def setQuery(self, query_getter):
        self._query_getter = query_getter
        self.refresh()

    def get_collection(self):
        if self._query_getter:
            return self._query_getter()
        return []


class XmlOpenTableView(OpenTableView):
    """
    It works exactly like a OpenTableView, but does not check that
    _entity_admin is effectively an EntityAdmin. It works well e.g. with
    XmlAdmin
    """

    def __init__(self, entity_admin):
        self._entity_admin = entity_admin


class XmlTableView(TableView):

    table_model = XmlCollectionProxy

    def create_table_model(self, admin):
        return self.table_model(admin,
                                lambda: [],
                                admin.get_columns)

    @QtCore.pyqtSlot(str)
    def startSearch(self, text):
        if self.admin.search_all_fields:
            search_fields = self.admin.list_display
        else:
            search_fields = self.admin.list_search
        text = unicode(text)
        def search_filter(xmllist):
            return xmllist.filter(search_fields, text)
        self.search_filter = search_filter
        self.rebuild_query()

    @QtCore.pyqtSlot(object)
    def _set_query(self, query_getter):
        self.table.model().setQuery(query_getter)
        self.table.clearSelection()
