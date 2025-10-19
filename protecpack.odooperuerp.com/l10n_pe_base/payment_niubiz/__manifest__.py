# -*- coding: utf-8 -*-
{
    'name': "Proveedor de pago: Niubiz",

    'summary': "Proveedor de pago: Niubiz",

    'description': """
Proveedor de pago: Niubiz
    """,

    'author': "CodLan - Harrison",
    'website': "https://www.codlan.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Payment Providers',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['payment', 'website_sale'],

    # always loaded
    'data': [
        'views/payment_views.xml',
        'views/payment_niubiz_templates.xml',
        'views/payment_templates.xml',
        'views/website_templates.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'assets': {
        'web.assets_frontend': [
            'payment_niubiz/static/src/**/*',
        ],
    },
    'license': 'Other proprietary',
}

