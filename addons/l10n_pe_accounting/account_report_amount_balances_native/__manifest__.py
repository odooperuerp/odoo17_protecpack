{
	'name': 'Balance de Comprobación-Hoja de Trabajo F12',
	'version': "17.0.0.1",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':[
		'account',
		'account_element',
		'report_formats',
		'one2many_search_widget',
		'unique_library_accounting_queries'],
	'description':'''
		Modulo de Balance de Comprobación-Hoja de Trabajo F12.
			> Balance de Comprobación-Hoja de Trabajo F12
		''',
	'data':[
		'security/ir.model.access.csv',
		'views/report_amount_balances_native_view.xml',
		'data/balance.category.column.native.csv',
	],
	'installable': True,
    'auto_install': False,
}
