# -*- coding: utf-8 -*-
{
    'name': 'Catálogos de SUNAT',
    'countries': ['pe'],
    'category': 'Accounting',
    'depends': ['base','account'],
    'version': '0.1',
    'summary': 'Catálogos de SUNAT',

    'description': """
    Este módulo permite la carga automática de los catálogos SUNAT , 
    tanto de tablas anexas a los libros electrónicos como a la facturación electrónica.
    """,

    'author': "CodLan, Alex Rodriguez",
    'website': "https://www.codlan.com",

    'data': [
        'security/ir.model.access.csv',
        'data/l10n.pe.sunat.table.csv',
        'data/l10n.pe.catalogs.sunat.csv',
        'views/l10n_pe_catalogs.xml',
        'views/search.xml',
    ],
    'license': 'OEEL-1',
}