{
	'name': 'SUNAT PLE Libro Diario-Mayor-Simplificado',
	'version': "17.0.0.1",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':[
		'account',
		'ple_base',
		'l10n_pe_account_document_extra_fields',
		'unique_library_accounting_queries'],
	'description':'''
		Modulo de reportes PLE de Libro Diario-Mayor-Simplificado.
			> Libro Diario-Mayor-Simplificado
		''',
	'data':[
		#'security/group_users.xml',
		'security/ir.model.access.csv',
		'views/ple_diary_view.xml',
		'views/ple_diary_line_view.xml',
		'views/wizard_printer_ple_diary_view.xml',
	],
	'installable': True,
    'auto_install': False,
}