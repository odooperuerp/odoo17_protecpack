# -*- coding: utf-8 -*-
{
    'name': 'Segunda moneda por empresa y campos auxiliares en ME',
    'version': '17.0.0.1',
    'category': '',
    'author': 'Franco Najarro - Dorniers Computer',
    'summary': 'Segunda moneda por empresa y campos auxiliares en ME',
    'website': '',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'views/res_company_view.xml',
        'views/account_move_line_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}