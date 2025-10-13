# -*- encoding: utf-8 -*-

{
    'name': 'Tipo de Cambio Especial para Pagos/Cobros y Transferencias',
    'summary': """
    	Tipo de Cambio Especial para Pagos/Cobros y Transferencias
    """,
    'version': '17.0.0.1',
    'category': 'Accounting',
    'description': """
       Tipo de Cambio Especial para Pagos/Cobros y Transferencias
    """,
    'author': 'Franco Najarro',
    'website': '',
    'depends': [
        'base',
        'account',
        'l10n_pe_account_document_extra_fields',
        'l10n_pe_catalogs_sunat',
        'l10n_pe_payment_method_sunat',],
    'data': [
        'views/account_payment_view.xml',
        'views/account_payment_register_view.xml',
        #'views/account_move_view.xml',
    ],
}
