{
	'name': 'CAMPOS TRIBUTARIOS PARA SUNAT PLE/SIRE',
	'version': "17.0.0.1",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':[
		'base',
		'contacts',
		'account',
		'l10n_pe_catalogs_sunat'],
	'description':'''
		'CAMPOS TRIBUTARIOS PARA SUNAT PLE/SIRE'
		> 
		''',
	'data':[
		'views/res_bank_view.xml',
		'views/res_country_view.xml',
		'views/res_currency_view.xml',
		'views/account_move_view.xml',

	],
	'installable': True,
    'auto_install': False,
}