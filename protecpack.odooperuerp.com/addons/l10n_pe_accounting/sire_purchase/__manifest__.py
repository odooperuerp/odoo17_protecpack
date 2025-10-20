{
	'name': 'SIRE SUNAT COMPRAS',
	'summary': 'SIRE SUNAT COMPRAS PERÚ',
	'version': "17.0.0.1",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':[
		'account',
		'l10n_pe_account_document_extra_fields',
		'sire_base'],
	'description':'''
		Modulo SIRE SUNAT COMPRAS
	''',
	'data':[
		'security/ir.model.access.csv',
		'views/sire_purchase_view.xml',
	],
	'installable': True,
    'auto_install': False,
}