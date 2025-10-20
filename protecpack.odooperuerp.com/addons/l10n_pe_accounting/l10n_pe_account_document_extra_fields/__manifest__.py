{
	'name': 'Campos adicionales en Asientos y Apuntes Contables. Pagos/Cobros con Cuenta destino manual',
	'version': "1.1.0",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':[
		'base',
		'sale',
		'purchase',
		'account',
		'l10n_pe_edi',
		'l10n_latam_invoice_document'],
	'description':'''
		Campos adicionales en Asientos y Apuntes Contables. Pagos/Cobros con Cuenta destino manual
			> Campos adicionales en Asientos y Apuntes Contables. Pagos/Cobros con Cuenta destino manual
		''',
	'data':[
		'security/res_groups.xml',
		'views/account_journal_view.xml',
		'views/account_move_view.xml',
		'views/account_move_line_view.xml',		
		'views/account_payment_view.xml',
	],
	'installable': True,
    'auto_install': False,
}