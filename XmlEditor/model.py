from sqlalchemy.types import Boolean, Integer
from XmlEditor.xml_admin import XmlEntity, XmlAdmin

class Person(XmlEntity):
    xml_path = 'Persons.Person'
    class types:
        age = Integer()
        male = Boolean()

    class Admin(XmlAdmin):
        verbose_name = 'Person'
        verbose_name_plural = 'Persons'
        list_display = ['name',
                        'surname',
                        'age',
                        'male',
                        ]

        form_display = list_display

