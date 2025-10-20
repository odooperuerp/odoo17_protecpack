{
	'name': 'SUNAT PLE-COMPRAS',
	'version': "13.0.3",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':['account','ple_base','l10n_pe_account_document_extra_fields','l10n_pe_detraccion'],
	'description':'''
		Modulo de reporte PLE de Compras.
			> PLE Compras
		''',
	'data':[
		#'security/group_users.xml',
		'security/ir.model.access.csv',
		'views/ple_purchase_view.xml',
		'views/ple_purchase_line_view.xml',
		'views/wizard_printer_ple_purchase_view.xml',
	],
	'installable': True,
    'auto_install': False,
}