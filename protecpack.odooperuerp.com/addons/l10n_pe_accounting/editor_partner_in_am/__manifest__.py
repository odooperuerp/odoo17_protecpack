{
    'name': 'Editor de Auxiliares en Asientos Contables',
    'version': '17.0.0.1',
    'category': '',
    'license': 'AGPL-3',
    'summary': "Editor de Auxiliares en Asientos Contables",
    'author': "Franco Najarro-Codlan",
    'website': '',
    'depends': ['account','editor_account_in_aml'],
    'data': [
        'security/ir.model.access.csv',
        'views/editor_partners_account_move_view.xml',
        ],
    'installable': True,
    'autoinstall': False,
}