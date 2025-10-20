{
	'name': 'SUNAT PLE-Inventarios Balances-Detalle Saldo Cuenta 50.Capital-Estructura Participación/Acciones',
	'version': "1.0.0",
	'author': 'Franco Najarro-Codlan',
	'website':'',
	'category':'',
	'depends':[
		'base',
		'account',
		'ple_base',
		'report_formats',
		'l10n_pe_shares_participations'],
	'description':'''
		Modulo de reportes PLE Inventarios Balances-Detalle Saldo Cuenta 50.Capital-Estructura Participación/Acciones.
			> PLE Inventarios Balances-Detalle Saldo Cuenta 50.Capital-Estructura Participación/Acciones
		''',
	'data':[
		'security/group_users.xml',
		'security/ir.model.access.csv',
		'views/ple_inventarios_balances_3_16_view.xml',
		'views/ple_inventarios_balances_3_16_line_view.xml',
		'views/wizard_printer_ple_inventarios_balances_3_16_view.xml',
	],
	'installable': True,
    'auto_install': False,
}