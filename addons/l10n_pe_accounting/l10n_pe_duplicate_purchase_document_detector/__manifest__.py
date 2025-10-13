{
	'name': 'Detector de Comprobantes de Compra Duplicados.',
	'version': "17.0.0.1",
	'author': 'Franco Najarro-Codlan',
	'website':'',
	'category':'',
	'depends':[
		'base',
		'account',
		'l10n_latam_invoice_document',
		'l10n_pe_account_document_extra_fields'],

	'description':'''
		Detector de Comprobantes de Compra Duplicados.
			> Detector de Comprobantes de Compra Duplicados.
		''',
	'data':[
		'views/account_move_view.xml',

	],
	'installable': True,
    'auto_install': False,
}