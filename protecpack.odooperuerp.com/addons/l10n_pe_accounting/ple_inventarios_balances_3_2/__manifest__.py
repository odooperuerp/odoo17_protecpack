{
	'name': 'SUNAT PLE-Inventarios Balances 3.2 - Detalle Saldo Cuenta 10',
	'version': "1.0.0",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':['base',
		'account',
		'ple_base',
		'unique_library_accounting_queries'],
	'description':'''
		Modulo de reportes PLE-Inventarios Balances 3.2 - Detalle Saldo Cuenta 10.
			> Libro PLE Inventarios y Balances 3.2
		''',
	'data':[
		'security/group_users.xml',
		'security/ir.model.access.csv',
		'views/ple_inventarios_balances_3_2_view.xml',
		'views/ple_inventarios_balances_3_2_line_view.xml',
		'views/wizard_printer_ple_inventarios_balances_3_2_view.xml',
	],
	'installable': True,
    'auto_install': False,
}