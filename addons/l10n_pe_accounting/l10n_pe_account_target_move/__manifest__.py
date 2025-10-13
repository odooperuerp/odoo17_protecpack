###############################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

{
    "name": "Asientos Destino",
    "version": "17.0.1.0.0",
    "author": "OPeru",
    "category": "Accounting",
    "summary": "Asiento destino automaticos al publicar un asiento.",
    "contributors": [
        "Soporte OPeru <soporte@operu.pe>",
    ],
    "website": "https://www.operu.pe/",
    "depends": ["account"],
    "data": [
        "data/action_server_account_target_massive.xml",
        "views/account_move_views.xml",
        "views/account_views.xml",
    ],
    "qweb": [],
    "images": [
        "static/description/banner.png",
    ],
    "installable": True,
    "live_test_url": "http://operu.pe/manuales",
    "license": "LGPL-3",
    "support": "modulos@operu.pe",
    "price": 9.00,
    "currency": "EUR",
    "sequence": 2,
}
