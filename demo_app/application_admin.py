from camelot.view.art import Icon
from camelot.admin.action.base import Action
from camelot.admin.section import Section, SectionItem
from xmlot.application_admin import XmlApplicationAdmin
from xmlot.entity import xmldump
import model

class DumpXmlAction(Action):

    def __init__(self, xml_root):
        self.xml_root = xml_root

    def gui_run(self, gui_context):
        xmldump(self.xml_root)
        print


class MyApplicationAdmin(XmlApplicationAdmin):
  
    name = 'Xml Editor'
    application_url = '...'
    help_url = '...'
    author = '...'
    domain = '...'
    xml_path = 'data.xml'

    def _dump(self):
        action = DumpXmlAction(self.xml_root)
        return SectionItem(action, self, 'dump xml')

    def get_sections(self):
        return [Section('tables',
                        self,
                        Icon('tango/22x22/actions/document-open.png'),
                        items = [self._item(model.Person),
                                 self._dump(),
                                 ]),
                ]
