{
	'name': 'SUNAT SIRE Base',
	'version': "1.0.2",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':[
		'account',
		'report_formats',
		'l10n_pe_account_document_extra_fields',
		'l10n_pe_edi_doc',
		'l10n_pe_ple_sire_base',],
	'description':'''
		Modulo Base SIRE SUNAT.
		> 
		''',
	'data':[
		'security/group_users.xml',
		'security/ir.model.access.csv',
		'views/sire_base_view.xml',
		'views/res_company_view.xml',

	],
	'installable': True,
    'auto_install': False,
}