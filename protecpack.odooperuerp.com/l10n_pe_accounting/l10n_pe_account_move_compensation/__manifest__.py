{
    'name': 'Registro de Compensación de Cuentas por Cobrar y Pagar.',
    'version': '17.0.0.1',
    'category': '',
    'license': 'AGPL-3',
    'summary': "Registro de Compensación de Cuentas por Cobrar y Pagar.",
    'author': "Franco Najarro",
    'website': '',
    'depends': ['account','l10n_pe_edi_doc','l10n_pe_account_document_extra_fields'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_compensation_view.xml',
        ],
    'installable': True,
    'autoinstall': False,
}
