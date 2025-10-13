{
	'name': 'SIRE SUNAT VENTAS',
	'summary': 'SIRE SUNAT VENTAS PERÚ',
	'version': "1.1.0",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':['account','l10n_pe_account_document_extra_fields','sire_base'],
	'description':'''
		Modulo SIRE SUNAT VENTAS
	''',
	'data':[
		'security/ir.model.access.csv',
		'views/sire_sale_view.xml',
	],
	'installable': True,
    'auto_install': False,
}