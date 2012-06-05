from camelot.admin.object_admin import ObjectAdmin
from camelot.admin.action.list_action import OpenFormView
from xmlot.view import XmlTableView
from xmlot.types import XmlRelation, PrimitiveType
from xmlot.entity import XmlEntity

class XmlAdmin(ObjectAdmin):

    TableView = XmlTableView
    list_action = OpenFormView()
    search_all_fields = False
    list_search = []

    def create_table_view(self, gui_context):
        return self.TableView(gui_context, self)

    def delete(self, obj):
        assert isinstance(obj, XmlEntity)
        elem = obj._elem
        parent = elem.getparent()
        parent.remove(elem)

    def copy(self, obj):
        from copy import deepcopy
        assert isinstance(obj, XmlEntity)
        newelem = deepcopy(obj._elem)
        return obj.__class__(newelem)

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
        xmltype = getattr(self.entity.types, field_name, None)
        if xmltype is None or isinstance(xmltype, PrimitiveType):
            sqltype = getattr(xmltype, 'sqltype', Unicode())
            get_attrs = _sqlalchemy_to_python_type_.get(sqltype.__class__, None)
            if get_attrs:
                attrs.update(get_attrs(sqltype))
        elif isinstance(xmltype, XmlRelation):
            target = xmltype.entity_cls
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
        #
        if getattr(xmltype, 'name', None):
            attrs['name'] = xmltype.name
        #
        forced_attrs = self.field_attributes.get(field_name, {})
        if 'choices' in forced_attrs:
            attrs['delegate'] = delegates.ComboBoxDelegate
            attrs['editable'] = True
            if isinstance(forced_attrs['choices'], list):
                choices_dict = dict(forced_attrs['choices'])
                attrs['to_string'] = lambda x : choices_dict[x]
        #
        attrs.update(forced_attrs)
        return attrs
