{
    "name":"Mejoras en layout de comprobantes de Venta en formato electrónico.",
    "summary":"Mejoras en layout de comprobantes de Venta en formato electrónico",
    "depends":[
        "base",
        "account",
        "l10n_pe_edi",
        "l10n_pe_edi_doc",
        "l10n_pe_retentions"
    ],
    "countries": ["pe"],
    "data": [
    	"views/account_move_view.xml",
        "views/report_invoice_document.xml",
    ],
    'license': 'LGPL-3',
}