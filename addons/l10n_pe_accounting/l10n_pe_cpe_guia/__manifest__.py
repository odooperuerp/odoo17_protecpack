# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

{
	'name': "Guia de Remisión Remitente SUNAT",

	'summary': """
		Guia de Remisión Remitente SUNAT - Perú""",

	'description': """
		Guia de Remisión Remitente SUNAT
	""",

	'author': "Franco Najarro-Codlan",
	'website': "",
	'category': 'Financial',
	'version': '17.0.0.1',
	'license': 'Other proprietary',
	'depends': [
		'stock',
		'account',
		'l10n_pe_edi',
		'stock_delivery',
		'l10n_pe_edi_stock',
	],
	'data': [
		'views/stock_view.xml',
		'report/report_guia.xml',
	],
	'installable': True,
}