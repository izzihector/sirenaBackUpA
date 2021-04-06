# -*- coding: utf-8 -*-

{
    'name': 'Auto Generate Lot/Serial Number',
    'version': '1.0',
    'category': 'Sale',
    'sequence': 6,
    'author': 'Webveer',
    'summary': "Allows you to automatically generate Lot/Serial number.",
    'description': """

=======================

Allows you to automatically generate Lot/Serial number.

""",
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'qweb': [
        # 'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/config1.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 25,
    'currency': 'EUR',
}
