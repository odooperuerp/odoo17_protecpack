{
	'name': 'Libro Diario-Mayor Multi-Moneda',
	'version': "17.0.0.1",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':[
		'base',
		'account',
		'analytic',
		'l10n_pe_account_document_extra_fields',
		'unique_library_accounting_queries'],
	'description':'''
		MÓDULO DE REPORTE LIBRO DIARIO-MAYOR MULTI-MONEDA.
			> LIBRO DIARIO-MAYOR MULTI-MONEDA
		''',
	'data':[
		'security/ir.model.access.csv',
		'views/diary_ledger_multi_currency_view.xml',
		'views/diary_ledger_multi_currency_line_view.xml',
	],
	'installable': True,
    'auto_install': False,
}