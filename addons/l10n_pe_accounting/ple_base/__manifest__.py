{
	'name': 'SUNAT PLE LIBROS BASE',
	'version': "1.0.2",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':[
		'base',
		'account',
		'report_formats',
		'l10n_pe_account_document_extra_fields',
		'l10n_pe_edi_doc',
		'one2many_search_widget',
		'l10n_pe_ple_sire_base',],
	'description':'''
		Modulo de reportes.
			> Base
		''',
	'data':[
		'security/group_users.xml',
		'security/ir.model.access.csv',
		'views/ple_base_view.xml',
		'views/wizard_printer_ple_base_view.xml',
	],
	'installable': True,
    'auto_install': False,
}