{
	'name': 'SUNAT PLE-Plan Contable-Diario-Simplificado',
	'version': "17.0.0.1",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':['account','ple_base'],
	'description':'''
		Modulo de reporte PLE Plan Contable utilizado.
			> Plan Contable del Libro Diario y Simplificado Utilizado
		''',
	'data':[
		#'security/group_users.xml',
		'security/ir.model.access.csv',
		'views/ple_diary_accounting_plan_view.xml',
		'views/ple_diary_accounting_plan_line_view.xml',
		'views/wizard_printer_ple_diary_accounting_plan_view.xml',
	],
	'installable': True,
    'auto_install': False,
}