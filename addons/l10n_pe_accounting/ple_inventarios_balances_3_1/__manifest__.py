{
	'name': 'SUNAT PLE-Inventarios y Balances 3.1 : Estado de Situación Financiera',
	'version': "1.0.0",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':['base','account',
		'ple_base',
		'unique_library_accounting_queries',
		'ple_financial_statement'
	],
	'description':'''
		Modulo de reportes PLE Inventarios Balances 3.1 : Estado de Situación Financiera.
			> SUNAT PLE-Inventarios y Balances 3.1 : Estado de Situación Financiera
		''',
	'data':[
		'security/group_users.xml',
		'security/ir.model.access.csv',
		'views/ple_inventarios_balances_3_1_view.xml',
		'views/ple_inventarios_balances_3_1_line_view.xml',
		'views/wizard_printer_ple_inventarios_balances_3_1_view.xml',
	],
	'installable': True,
    'auto_install': False,
}