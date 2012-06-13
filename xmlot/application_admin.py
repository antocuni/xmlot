import py
from datetime import datetime
from PyQt4.QtCore import Qt
from PyQt4 import QtGui
from camelot.admin.application_admin import ApplicationAdmin
from camelot.admin.action.base import Action
from camelot.admin.section import SectionItem
from camelot.view.art import Icon
from xmlot.entity import xmltostring
from xmlot.view import XmlOpenTableView


class XmlApplicationAdmin(ApplicationAdmin):

    xml_path = None # needs to be overridden
    make_backups = True
    
    def __init__(self):
        from lxml import objectify
        ApplicationAdmin.__init__(self)
        self.xml_path = py.path.local(self.xml_path)
        self.xml_root = objectify.fromstring(self.xml_path.read())
        self.backup_done = False

    def do_backup_maybe(self):
        if not self.make_backups or self.backup_done:
            return
        timestamp = datetime.now().strftime('%Y-%m-%d %H.%M')
        name = '%s (backup of %s)' % (self.xml_path.purebasename, timestamp)
        backup = self.xml_path.new(purebasename=name)
        self.xml_path.copy(backup)
        self.backup_done = True

    def save(self):
        xmldoc = xmltostring(self.xml_root)
        self.xml_path.write(xmldoc)

    def _item(self, cls):
        admin = self.get_related_admin(cls)
        assert admin is not None
        action = XmlOpenTableView(admin)
        return SectionItem(action, self)

    def get_toolbar_actions( self, toolbar_area ):
        if toolbar_area == Qt.TopToolBarArea:
            return [SaveXml()] + self.edit_actions + self.change_row_actions + \
                self.export_actions


class SaveXml(Action):

    shortcut = QtGui.QKeySequence.Save
    icon = Icon('tango/16x16/devices/media-floppy.png')
    tooltip = "Salva le modifiche su disco"
    verbose_name = 'Salva'
    
    def gui_run(self, gui_context):
        app_admin = gui_context.admin.get_application_admin()
        app_admin.do_backup_maybe()
        app_admin.save()
