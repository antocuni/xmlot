from sqlalchemy.types import Boolean, Integer
from XmlEditor.xml_admin import XmlEntity, XmlList, XmlAdmin, XmlRelatedListWrapper

def make_static_choices(*values):
    result = [(None, u'')] + list(values)
    def choices(obj):
        return result
    return choices


class Job(XmlEntity):
    xml_path = 'Jobs'
    xml_tag = 'Job'

    class Admin(XmlAdmin):
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        list_display = ['title']
        form_display = list_display

class Uncle(XmlEntity):
    xml_tag = 'Uncle'

    class Admin(XmlAdmin):
        list_display = ['name', 'age', 'relative']
    


class Person(XmlEntity):
    xml_path = 'Persons'
    xml_tag = 'Person'
    class types:
        age = Integer()
        male = Boolean()
        jobs = XmlList(Job)
        uncles = XmlList(Uncle)

    @property
    def uncles(self):
        root = self._elem.getroottree().getroot()
        elems = []
        for elem in root.Uncles.Uncle:
            if elem.relative == self.name:
                elems.append(elem)
        field_values = dict(relative = self.name)
        return XmlRelatedListWrapper(root.Uncles, Uncle, elems, field_values)


    class Admin(XmlAdmin):
        verbose_name = 'Person'
        verbose_name_plural = 'Persons'
        list_display = ['name',
                        'surname',
                        'age',
                        'city',
                        'male',
                        ]

        form_display = list_display + ['uncles', 'jobs']

        field_attributes = {
            'city': dict(
                choices = make_static_choices((u'Mouseton', u'Mouseton'),
                                              (u'Duckburg', u'Duckburg')
                                              ),
                )
            }
