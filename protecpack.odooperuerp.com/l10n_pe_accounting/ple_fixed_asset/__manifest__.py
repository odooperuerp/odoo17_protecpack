{
	'name': 'SUNAT PLE-Registro de Activos Fijos',
	'version': "17.0.0.1",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':[
		'account',
		'ple_base',
		'account_asset',
		'l10n_pe_intangible_asset'],
	'description':'''
		Modulo de reportes PLE de Activos Fijos.
			> Libro de Activos Fijos
		''',
	'data':[
		#'security/group_users.xml',
		'security/ir.model.access.csv',
		'views/account_asset_asset_view.xml',
		'views/ple_fixed_asset_view.xml',
		'views/ple_fixed_asset_line_view.xml',
		'views/wizard_printer_ple_fixed_asset_view.xml',
	],
	'installable': True,
    'auto_install': False,
}