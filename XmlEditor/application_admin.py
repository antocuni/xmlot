from camelot.view.art import Icon
from camelot.admin.application_admin import ApplicationAdmin
from camelot.admin.section import Section, SectionItem

from XmlEditor.xml_admin import XmlOpenTableView
from XmlEditor import model




class MyApplicationAdmin(ApplicationAdmin):
  
    name = 'Xml Editor'
    application_url = '...'
    help_url = '...'
    author = '...'
    domain = '...'

    def __init__(self):
        from lxml import objectify
        ApplicationAdmin.__init__(self)
        with open('data.xml') as xml:
            self.xml_root = objectify.fromstring(xml.read())

    def _item(self, cls):
        admin = self.get_related_admin(cls)
        assert admin is not None
        action = XmlOpenTableView(admin)
        return SectionItem(action, self)

    def get_sections(self):
        return [Section('tables',
                        self,
                        Icon('tango/22x22/actions/document-open.png'),
                        items = [self._item(model.Person),
                                 ]),
                ]
