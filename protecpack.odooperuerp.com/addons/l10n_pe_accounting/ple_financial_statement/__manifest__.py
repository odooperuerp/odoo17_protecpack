{
	'name': 'SUNAT PLE - RUBROS PARA LOS ESTADOS FINANCIEROS SUNAT',
	'version': "17.0.0.1",
	'author': 'Franco Najarro-Codlan',
	'website':'',
	'category':'',
	'depends':['base','account','ple_base'],
	'description':'''
		Modulo de Rubros de los estados Financieros PLE para Libros de Inventarios y Balances.
			> Modulo de Rubros de los estados Financieros PLE para Libros de Inventarios y Balances.
		''',
	'data':[
		'data/economic_sector_sunat_data.xml',
		'data/group_heading_financial_statement_data.xml',
		'data/financial_statement_heading_data.xml',
		'data/financial_statement_heading_line_data.xml',
		'security/group_users.xml',
		'security/ir.model.access.csv',
		'views/res_company_view.xml',
		'views/financial_statement_heading_line_view.xml',
		'views/financial_statement_heading_view.xml',
	],
	'installable': True,
    'auto_install': False,
}