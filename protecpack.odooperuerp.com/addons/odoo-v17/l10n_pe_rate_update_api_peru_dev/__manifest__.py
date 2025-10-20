{
    "name": "Perú - Actualizar Tasas Api Peru Dev",
    "countries": ["pe"],
    "version": "17.0.1.2.2",
    "author": "Leo Daniel FS",
    "website": "https://www.linkedin.com/in/leo-daniel-flores",
    "summary": "Obtiene y actualiza las tasas de cambio con Api Peru Dev",
    "description": """
Este módulo obtiene y actualiza las tasas de cambio con el proveedor Api Peru Dev.
Para las monedas USD Y EUR.
""",
    "category": "Accounting/Localizations",
    "depends": [
        "invoice_currency_rate_update",
    ],
    "data": [
        "sql/update_module_type.sql",
        "views/res_currency_rate_provider.xml",
    ],
    "module_type": "official",
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
}
