{
    'name': 'Registro de Rendición de Caja Chica',
    'version': '17.0.0.1',
    'category': '',
    'license': 'AGPL-3',
    'summary': "Registro de Rendición de Caja Chica",
    'author': "Franco Najarro",
    'website': '',
    'depends': [
        'base',
        'account',
        'mail',
        'l10n_pe_account_document_extra_fields',
        'l10n_pe_edi_doc'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_rendicion_caja_chica_view.xml',
        ],
    'installable': True,
    'autoinstall': False,
}
