{
	'name': 'Voucher Contable en PDF A4 - Formato standard.',
	'version': "17.0.0.1",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':[
		'base',
		'sale',
		'purchase',
		'account',
		'l10n_pe_edi',
		'l10n_latam_invoice_document',
		'l10n_pe_edi_doc',
		'l10n_pe_account_document_extra_fields',
		'l10n_pe_company_second_currency',
		],
	'description':'''
		Voucher Contable en PDF A4 - Formato standard.
			> Voucher Contable en PDF A4 - Formato standard.
		''',
	'data':[
		'report/account_voucher_a4.xml',
		'report/report.xml',
	],
	'installable': True,
    'auto_install': False,
}