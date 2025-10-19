{
    "name":"Consulta RUC/DNI desde Punto de Venta",
    "author":"Daniel Moreno <daniel@codlan.com>",
    "version": "17.0.1.0",
    "website": "https://www.codlan.com",
    "depends":[
        "l10n_pe",
        "point_of_sale",
        "bo_pe_partner"
    ],
    "license": "OPL-1",
    "countries": ["pe"],
    "data": [
        "security/res_groups.xml",
        "data/res_partner.xml"
    ],
    "installable": True,
    "assets": {
        "point_of_sale._assets_pos": [
            "l10n_pe_pos_vat/static/src/**/*"
        ],
    },
}