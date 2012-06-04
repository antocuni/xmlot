from sqlalchemy.types import Boolean, Integer
from XmlEditor.xml_admin import XmlEntity, XmlList, XmlAdmin

class Job(XmlEntity):
    xml_path = 'Jobs'
    xml_tag = 'Job'

    class Admin(XmlAdmin):
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        list_display = ['title']
        form_display = list_display


class Person(XmlEntity):
    xml_path = 'Persons'
    xml_tag = 'Person'
    class types:
        age = Integer()
        male = Boolean()
        jobs = XmlList(Job)

    class Admin(XmlAdmin):
        verbose_name = 'Person'
        verbose_name_plural = 'Persons'
        list_display = ['name',
                        'surname',
                        'age',
                        'male',
                        ]

        form_display = list_display + ['jobs']


