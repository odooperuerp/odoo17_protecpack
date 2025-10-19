{
    'name': 'Editor de Cuentas en Apuntes Contables',
    'version': '17.0.0.1',
    'category': '',
    'license': 'AGPL-3',
    'summary': "Editor de Cuentas en Apuntes Contables",
    'author': "Franco Najarro",
    'website': '',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/editor_account_aml_view.xml',
        ],
    'installable': True,
    'autoinstall': False,
}