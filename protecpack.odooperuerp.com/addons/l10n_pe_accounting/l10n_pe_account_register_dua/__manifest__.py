{
    'name': 'Registro de DUA',
    'version': '17.0.0.1',
    'category': '',
    'license': 'AGPL-3',
    'summary': "Registro de DUA",
    'author': "Franco Najarro-Codlan",
    'website': '',
    'depends': [
        'base',
        'account',
        'l10n_pe_account_document_extra_fields',
        'l10n_pe_edi_doc'],
    'data': [
        'security/ir.model.access.csv',
        'views/template_dua_informacion_anotable_view.xml',
        'views/template_dua_informacion_referencial_view.xml',
        'views/account_registro_dua_view.xml',
        ],
    'installable': True,
    'autoinstall': False,
}
