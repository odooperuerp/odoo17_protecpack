{
    'name': 'Facturas/Boletas/Notas de Crédito desde Punto de Venta',
    'description': 'Selecciona que tipo de comprobante de venta: Facturas, Boletas y Notas de crédito deseas emitir desde el punto de venta.',
    'author': 'Christian Bravo <christian@codlan.com>',
    'version': '17.0.1.0',
    'website': 'https://www.codlan.com',
    'license': 'OPL-1',
    'depends': [
        'base',
        'account',
        'stock_account',        
        'point_of_sale',
        'l10n_pe',
        'l10n_pe_pos_vat',
        'l10n_pe_edi_doc',
        'l10n_latam_invoice_document'
    ],
    'countries': ['pe'],
    'data': [
        'security/res_groups.xml',
        'views/account_move_views.xml',
        'views/res_config_settings_views.xml',
        'templates/report_account_move.xml'
    ],
    "installable": True,
    'assets': {
        'point_of_sale._assets_pos': [
            'l10n_pe_pos_base/static/src/**/*',
        ],
    },
    'auto_install': False,
}