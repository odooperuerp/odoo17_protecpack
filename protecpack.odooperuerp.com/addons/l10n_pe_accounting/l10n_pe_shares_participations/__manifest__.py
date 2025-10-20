{
	'name': 'Registro de Acciones y Participaciones',
	'version': "17.0.0.1",
	'author': 'Franco Najarro-Codlan',
	'website':'',
	'category':'Codlan',
	'depends':[
		'base',
		'account',
		'l10n_pe_catalogs_sunat',
		'ple_base'],
	'description':'''
		Modulo de Registro de Acciones y Participaciones.
			> Libro de Acciones y Participaciones
		''',
	'data':[
		'security/group_users.xml',
		'security/ir.model.access.csv',
		'views/shares_participations_view.xml',
		'views/shares_participations_line_view.xml',
	],
	'installable': True,
    'auto_install': False,
}