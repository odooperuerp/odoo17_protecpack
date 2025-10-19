{
    "name":"Formato de impresión compacto",
    "description":"Formato de impresión con sección de cliente compacto.",
    "author":"Daniel Moreno <daniel@codlan.com>",
    "version": "17.0.1.0",
    "license": "OPL-1",
    "website": "https://www.codlan.com",
    "depends":[
        "base",
        "web",
        "account",
        "sale",
        "purchase",
        "stock",
        "stock_account",
        "l10n_pe_edi",
        "l10n_pe_edi_stock"
    ],
    "data": [
        "security/res_groups.xml",
        "views/view_res_company.xml",
        "views/view_sale_order.xml",
        "views/view_account_move.xml",
        "views/view_account_journal.xml",
        "templates/external_layout_header_compact.xml",
        "templates/report_invoice_document.xml",
        "templates/report_saleorder_document.xml",
        "templates/report_purchase_order.xml",
        "templates/report_saleorder_document_hide_subtotals.xml",
        "templates/report_invoice_document_hide_subtotals.xml",
        "templates/report_delivery_document.xml"
    ],
    'assets':{
        'web.report_assets_common': [
                'external_layout_header_compact/static/src/scss/report.scss'
            ]
    }
}