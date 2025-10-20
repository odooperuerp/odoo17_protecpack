{
    "name":"Generación de XML y métodos de recuperación de XML",
    "summary":"Módulo con clases para la generación de XML y recuperación de CDR para los documentos: Factura, Boleta, Notas asociadas, Anulación, Resumen diario",
    "depends":[
        "base",
        "sale",
        "account",
        "product",
        "account_edi",
        "l10n_latam_invoice_document",
        "l10n_pe",
        "l10n_pe_edi",
        "l10n_pe_edi_stock",
        "account_edi_ubl_cii",
        "external_layout_header_compact"
    ],
    "author":"Daniel Moreno <daniel@codlan.com>",
    "countries": ["pe"],
    "version": "17.0.1.0",
    "website": "https://www.codlan.com",
    "data": [
        "security/ir_model_access.xml",
        "data/l10n_pe_ubl.xml",
        "data/l10n_pe_edi_stock.xml",
        "views/view_res_company.xml",
        "views/view_account_move.xml",
        "views/view_sale_order.xml",
        "views/view_res_partner_bank.xml",
        "views/view_stock_picking.xml",
        "views/view_res_partner.xml",
        "templates/report_invoice_document.xml",
        "templates/report_saleorder_document.xml",
        "templates/report_stock_picking.xml"
    ],
    "installable": True,
    "license": "OPL-1"
}



