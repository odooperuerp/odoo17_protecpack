{
	'name': 'SUNAT PLE-Libro Caja y Bancos',
	'version': "17.0.0.1",
	'author': 'Franco Najarro-Codlan',
	'website':'',
	'category':'Accounting',
	'depends':[
		'account',
		'ple_base',
		'l10n_pe_account_document_extra_fields',
		'l10n_pe_payment_method_sunat',
		#'extra_account_move_line'
		],
	'description':'''
		Modulo de reportes PLE de Libro Caja y Bancos.
			> PLE Libro Caja y Bancos
		''',
	'data':[
		'security/ir.model.access.csv',
		'views/account_journal_view.xml',
		'views/ple_diary_cash_box_and_banks_view.xml',
		'views/ple_diary_cash_box_and_banks_line_view.xml',
		'views/wizard_printer_ple_diary_cash_box_and_banks_view.xml',
	],
	'installable': True,
    'auto_install': False,
}