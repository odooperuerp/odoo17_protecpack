{
    "name": "Reportes de Cuentas por Cobrar y Pagar a Fecha Actual",
    'version': "1.0.0",
    'author': 'Franco Najarro-Codlan',
    'website':'',
    'category':'Accounting',
    'description':'''
        Reporte de Cuentas por Cobrar y Pagar a Fecha Actual.
        ''',
    "depends": [
        'base',
        'account',
        'l10n_pe_account_document_extra_fields'],
    "data": [
        'security/ir.model.access.csv',
        'views/account_payable_report_current_date_line_view.xml',
        'views/account_receivable_report_current_date_line_view.xml',
        'views/wizard_account_payable_report_current_date_view.xml',
        'views/wizard_account_receivable_report_current_date_view.xml',

    ]
}



