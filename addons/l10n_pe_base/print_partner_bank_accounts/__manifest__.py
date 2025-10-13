{
    "name": "Imprimir Ctas bancarias",
    "version": "1.0",
    "description": "Visualización de ctas bancarias de compañía en formatos pdf",
    "summary": """
    - Check de validación para mostrar en pdf.
    - Visualización de ctas bancarias en formato de cotización
    - Visualización de ctas bancarias en formato de factura
    """,
    "author": "Codlan - Christian Bravo",
    "website": "https://codlan.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "contacts",
        "account",
        "sale"
    ],
    "data": [
        "views/res_partner.xml",
        "views/res_partner_bank.xml",
        "reports/report_invoice_document.xml",
        "reports/report_saleorder_document.xml"
    ],
    "auto_install": False,
    "application": False,
}