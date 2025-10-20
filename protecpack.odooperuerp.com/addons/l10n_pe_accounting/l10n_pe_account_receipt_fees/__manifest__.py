{
    'name': 'Contabilidad y Reporte de Recibos por Honorarios',
    "summary": "Contabilidad y Reporte de Recibos por Honorarios",
    'description': """
        Generar el reporte de Recibo por Honorarios.\n
        Configuración:\n
        Ir a Ajustes / Facturación ==> Registrar la Cuenta Contable de Retención de 4ta Categoría.\n
        Uso:\n
        En el Treeview de Comprobantes de Proveedores, se visualizará el Monto de Retención\n
        Para exportar el reporte de Honorarios, ir a Facturación / Informes
    """,
    'version': '17.0.0.0',
    'category': 'Accounting',
    'author': "Franco Najarro-Codlan",
    'website': '',
    'license': 'AGPL-3',

    'depends': [
        'base',
        'account',
        'l10n_pe_account_receivable_payable_me',
        'l10n_pe_account_document_extra_fields',
        'report_formats'],

    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_view.xml',
        'views/account_move_view.xml',
        'views/wizard_receipt_of_fees_report_view.xml',
    ],
    'active': False,
    'installable': True
}
