# -*- coding: utf-8 -*-
{
    'name': "Purchase Report",

    'summary': "OC / OS / OI",

    'description': """
Diseño de formatos:
- Orden de compra
- Orden de servicio
- Orden de importación
    """,

    'author': "CodLan - Harrison",
    'website': "https://www.codlan.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory/Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'external_layout_header_compact'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/purchase_order_views.xml',
        'report/purchase_order_templates.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'Other proprietary',
}

