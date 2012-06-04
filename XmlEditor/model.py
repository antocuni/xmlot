from sqlalchemy.types import Boolean, Integer
from XmlEditor.xml_admin import XmlEntity, XmlAdmin, XmlList

class Job(XmlEntity):
    xml_path = None

    class Admin(XmlAdmin):
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        list_display = ['title']
        form_display = list_display


class Person(XmlEntity):
    xml_path = 'Persons.Person'
    class types:
        age = Integer()
        male = Boolean()
        jobs = XmlList('Jobs.Job', Job)

    class Admin(XmlAdmin):
        verbose_name = 'Person'
        verbose_name_plural = 'Persons'
        list_display = ['name',
                        'surname',
                        'age',
                        'male',
                        ]

        form_display = list_display + ['jobs']


