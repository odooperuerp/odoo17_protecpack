{
	'name': 'Generador de Transacciones de Extracto Bancario',
	'version': "17.0.0.1",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends': [
		'base',
		'account',
		'l10n_pe_account_document_extra_fields',
		'account_accountant',],
	'description':'''
		Modulo Generador de Transacciones de Extracto Bancario.
			> Generador de Transacciones de Extracto Bancario
		''',
	'data':[
		'security/ir.model.access.csv',
		'views/account_move_line_view.xml',
		'views/account_bank_statement_line_view.xml',
		'views/account_bank_statement_automatic_wizard_view.xml',
		'views/account_bank_statement_line_wizard_view.xml',
		'views/account_bank_statement_view.xml',
	],
	'installable': True,
	'auto_install': False,
}