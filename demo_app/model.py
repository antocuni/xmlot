from xmlot.admin import XmlAdmin, DumpXmlAction
from xmlot.entity import XmlEntity
from xmlot.types import XmlList, XmlOneToMany, Integer, Boolean, Unicode, Float

def make_static_choices(*values):
    result = [(None, u'')] + list(values)
    def choices(obj):
        return result
    return choices

class MyEntity(XmlEntity):
    xmlns = 'http://foo.bar'


class Job(MyEntity):
    xml_path = 'Jobs'
    xml_tag = 'Job'

    class Admin(XmlAdmin):
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        list_display = ['title']
        form_display = list_display

class Uncle(MyEntity):
    xml_path = 'Uncles'
    xml_tag = 'Uncle'

    class Admin(XmlAdmin):
        list_display = ['name', 'age', 'relative']
    


class Person(MyEntity):
    xml_path = 'Persons'
    xml_tag = 'Person'
    class types:
        age = Integer()
        male = Boolean()
        jobs = XmlList('jobs', Job)
        uncles = XmlOneToMany('uncles', Uncle, primary_key='name', foreign_key='relative')

    class Admin(XmlAdmin):
        verbose_name = 'Person'
        verbose_name_plural = 'Persons'
        list_display = ['name',
                        'surname',
                        'age',
                        'city',
                        'male',
                        ]

        form_actions = [DumpXmlAction()]
        form_display = list_display + ['uncles', 'jobs']

        field_attributes = {
            'city': dict(
                choices = make_static_choices((u'Mouseton', u'Mouseton'),
                                              (u'Duckburg', u'Duckburg')
                                              ),
                )
            }
