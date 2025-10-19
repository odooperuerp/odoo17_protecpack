{
    'name': 'Invoice Break Currency Rate',
    'version': '17.0.1.0.5',
    "author": "Leo Daniel FS",
    "website": "https://www.linkedin.com/in/leo-daniel-flores",
    'summary': 'Record more than one daily rate',
    'description': """
This module allows you to record more than one daily rate.
""",
    'category': 'Invoicing/Invoicing',
    'depends': [
        # Odoo community
        'base',
    ],
    'data': [
        'sql/update_module_type.sql',
    ],
    'module_type': 'official',
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
}
