{
    "name": "Consulta de Comprobantes de pago electrónico",
    "data":[
      "templates/view_form_consulta_cpe.xml"
    ],
    "countries":[
        "pe"
    ],
    "depends":[
        "base",
        "web",
        "l10n_pe_edi",
    ],
    "installable": True,
    "assets": {
        "web.assets_frontend": [
            "l10n_pe_consulta_cpe/static/src/js/consulta_cpe.js"
        ]
    }
}