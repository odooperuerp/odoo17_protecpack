{
    'name': 'Editor de Periodos en Asientos Contables',
    'version': '1.0.0',
    'category': '',
    'license': 'AGPL-3',
    'summary': "Editor de Periodos en Asientos Contables",
    'author': "Franco Najarro",
    'website': '',
    'depends': ['account','l10n_pe_account_period_pe','editor_account_in_aml'],
    'data': [
        'security/ir.model.access.csv',
        'views/editor_periods_account_move_view.xml',
        ],
    'installable': True,
    'autoinstall': False,
}
