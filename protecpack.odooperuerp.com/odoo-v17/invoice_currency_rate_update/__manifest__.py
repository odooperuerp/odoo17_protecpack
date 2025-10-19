{
    "name": "Invoice Currency Rate Update",
    "version": "17.0.1.4.4",
    "author": "Leo Daniel FS",
    "website": "https://www.linkedin.com/in/leo-daniel-flores",
    "category": "Invoicing/Invoicing",
    "summary": "Update exchange rates",
    "description": """
This module provides a basis for creating exchange rate providers.
""",
    "depends": [
        # Odoo community
        "base",
        "mail",
        "account",
        "invoice_break_currency_rate",
    ],
    "data": [
        "sql/update_module_type.sql",
        "data/cron.xml",
        "security/ir.model.access.csv",
        "security/res_currency_rate_provider.xml",
        "views/res_currency_rate.xml",
        "views/res_currency_rate_provider.xml",
        "views/res_config_settings.xml",
        "wizards/res_currency_rate_update_wizard.xml",
    ],
    "module_type": "official",
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
}
