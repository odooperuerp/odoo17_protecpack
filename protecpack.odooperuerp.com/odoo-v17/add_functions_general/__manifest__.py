# -*- coding: utf-8 -*-
{
    'name': "Agregar Requerimientos de clientes",

    'summary': """
        Add new fields required by clients
    """,

    'description': """
        Add new fields required by clients:
        - Calculate profit percentage based on the standard cost.
        - Add brand and internal code to each product.
        - Add ABC category to customers.
        - Selections of atention contact from his enterprise contact.
        - Format list "comprobantes de ventas".
    """,

    'author': "odooperuerp",
    'website': "odooperuerp.com",

    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','product','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        #'views/corretaje.xml',
    ],
    # only loaded in demonstration mode
    'demo_xml': [],
    'active':True,
    'installable':True,
}
