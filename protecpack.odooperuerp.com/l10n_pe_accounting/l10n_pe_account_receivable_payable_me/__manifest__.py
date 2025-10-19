{
	'name': 'Configuraciones de Contabilidad en Moneda Extranjera-Recibos por Honorarios',
	'version': "17.0.0.1",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':['base','account','purchase','sale'],
	'description':'''
		Configuraciones de Contabilidad en Moneda Extranjera.
			> Configuraciones de Contabilidad en Moneda Extranjera
		''',
	'data':[
		'views/res_config_settings_view.xml',
		'views/res_partner_view.xml',

	],
	'installable': True,
    'auto_install': False,
}