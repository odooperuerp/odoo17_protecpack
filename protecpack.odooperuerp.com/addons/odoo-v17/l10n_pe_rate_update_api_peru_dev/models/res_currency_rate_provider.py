import logging
from collections import defaultdict
from datetime import datetime

import requests
import pytz

from odoo import fields, models, _, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

MONEDAS = {"USD": "Dólar"} # "EUR": "Euro"
PERU_TZ = pytz.timezone("America/Lima")


class ResCurrencyRateProvider(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("api_peru_dev", "Api Peru Dev")],
        ondelete={"api_peru_dev": "set default"},
    )
    api_peru_dev_token = fields.Char(
        string="API Peru Dev Token", 
        help="Token de autenticación para Api Peru Dev",
    )

    @api.onchange('service')
    def _onchange_service_api_peru_dev(self):
        if self.service != "api_peru_dev":
            self.api_peru_dev_token = False

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "api_peru_dev":
            return super()._get_supported_currencies()
        return list(MONEDAS.keys())

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "api_peru_dev":
            return super()._obtain_rates(base_currency, currencies, date_from, date_to)

        if not self.api_peru_dev_token:
            raise UserError(
                _(
                    "Por favor, configure el token de API en el proveedor de tipo de cambio."
                )
            )

        content = defaultdict(dict)

        # Obtenemos la fecha actual en la zona horaria de Perú
        current_date = datetime.now(PERU_TZ).date()

        available_currency_names = currencies

        for currency_name in available_currency_names:
            if currency_name in MONEDAS:
                rate_data = self._get_rate_from_api_peru_dev(current_date, currency_name)
                date_str = current_date.isoformat()

                if rate_data:
                    is_invoice_purchase_exchange_rate_installed = self._is_invoice_purchase_exchange_rate_installed()

                    sale_rate = rate_data.get("venta")
                    purchase_rate = rate_data.get("compra")

                    if currency_name not in content[date_str]:
                        content[date_str][currency_name] = {}

                    if not sale_rate and not purchase_rate:
                        _logger.warning(f"No se encontraron tasas de venta o compra para {currency_name} en la fecha {date_str}")
                        continue

                    if is_invoice_purchase_exchange_rate_installed:
                        if sale_rate:
                            rate_value = 1.0 / sale_rate
                            content[date_str][currency_name]["sale"] = rate_value
                        if purchase_rate:
                            rate_value = 1.0 / purchase_rate
                            content[date_str][currency_name]["purchase"] = rate_value
                    else:
                        if sale_rate:
                            rate_value = 1.0 / sale_rate
                            content[date_str][currency_name]["sale"] = rate_value
                else:
                    _logger.warning(f"No se recibieron datos para la moneda {currency_name} en la fecha {date_str}")
        return content

    def _get_rate_from_api_peru_dev(self, date, currency_name):
        url = "https://apiperu.dev/api/tipo_de_cambio"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_peru_dev_token}",
        }
        payload = {
            "fecha": date.strftime("%Y-%m-%d"), 
            "moneda": currency_name
        }
        try:
            response = requests.post(
                url, json=payload, headers=headers
            )
            response.raise_for_status()
            data = response.json()
            if data["success"]:
                return data["data"]
            else:
                _logger.warning(
                    f"Error al obtener el tipo de cambio: {data.get('message', 'Error desconocido')}"
                )
                return None
        except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError) as e:
            _logger.error(f"Error al conectar con la API: {str(e)}")
            return None

    @api.model
    def _is_invoice_purchase_exchange_rate_installed(self):
        return bool(
            self.env['ir.module.module']
            .sudo()
            .search([('name', '=', 'invoice_purchase_exchange_rate'), ('state', '=', 'installed')])
        )
