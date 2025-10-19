import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResCurrencyRateProvider(models.Model):
    _name = "res.currency.rate.provider"
    _description = "Currency Rates Provider"
    _inherit = ["mail.thread"]
    _order = "name"

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_name = fields.Char(
        string="Currency Name", related="company_id.currency_id.name"
    )
    active = fields.Boolean(default=True)
    service = fields.Selection(
        string="Provider",
        selection=[("none", "None")],
        default="none",
        required=True,
    )
    available_currency_ids = fields.Many2many(
        string="Available Currencies",
        comodel_name="res.currency",
        compute="_compute_available_currency_ids",
    )
    currency_ids = fields.Many2many(
        string="Currencies",
        comodel_name="res.currency",
        column1="provider_id",
        column2="currency_id",
        required=True,
        help="Currencies to be updated by this provider",
    )
    name = fields.Char(compute="_compute_name", store=True)
    interval_type = fields.Selection(
        string="Scheduled Update Interval Unit",
        selection=[
            ("minutes", "Minute(s)"),
            ("hours", "Hour(s)"),
            ("days", "Day(s)"),
            ("weeks", "Week(s)"),
            ("months", "Month(s)")
        ],
        default="days",
        required=True,
    )
    interval_number = fields.Integer(
        string="Scheduled Update Interval", default=1, required=True
    )
    update_schedule = fields.Char(compute="_compute_update_schedule")
    last_successful_run = fields.Datetime(string="Last Successful Update")
    next_run = fields.Datetime(
        string="Next Scheduled Update", default=fields.Datetime.now, required=True
    )
    unique_exchange_rate_per_day = fields.Boolean(
        string='Unique Exchange Rate Per Day',
        default=True,
        help="If this option is enabled, a daily exchange rate will always be created "
        "for each currency when running the query. Remember that you can also record "
        "multiple daily exchange rates for each currency manually, this option will only "
        "prevent duplication for this query flow, not for manual records. If this option "
        "is disabled, it will always try to create a new rate for each query."
    )

    _sql_constraints = [
        (
            "service_company_id_uniq",
            "UNIQUE(service, company_id)",
            "This provider has already been setup in this company.",
        ),
        (
            "valid_interval_number",
            "CHECK(interval_number > 0)",
            "Scheduled update interval must be strictly positive.",
        ),
    ]

    @api.depends("service")
    def _compute_name(self):
        for provider in self:
            provider.name = dict(self._fields["service"].selection).get(provider.service)

    @api.depends("active", "interval_type", "interval_number")
    def _compute_update_schedule(self):
        for provider in self:
            if not provider.active:
                provider.update_schedule = _("Inactive")
                continue
            interval_display = dict(self._fields["interval_type"].selection).get(provider.interval_type)
            provider.update_schedule = _("%(number)s %(type)s") % {
                "number": provider.interval_number,
                "type": interval_display,
            }

    @api.depends("service")
    def _compute_available_currency_ids(self):
        Currency = self.env["res.currency"]
        for provider in self:
            provider.available_currency_ids = Currency.search(
                [("name", "in", provider._get_supported_currencies())]
            )

    def _update(self, date_from, date_to, newest_only=False):
        def get_or_create_currency_rate(currency, exchange_rate, rate):
            is_invoice_purchase_exchange_rate_installed = self._is_invoice_purchase_exchange_rate_installed()
            rate_data = {
                "rate": provider._process_rate(currency, rate),
                "provider_id": provider.id,
            }
            if provider.unique_exchange_rate_per_day:
                domain = [
                    ("company_id", "=", provider.company_id.id),
                    ("currency_id", "=", currency.id),
                    ("name", "=", rate_date),
                ]
                if is_invoice_purchase_exchange_rate_installed:
                    domain.append(("exchange_rate", "=", exchange_rate))
                record = CurrencyRate.search(domain, limit=1)
                if record:
                    record.write(rate_data)
                else:
                    rate_data.update({
                        "company_id": provider.company_id.id,
                        "currency_id": currency.id,
                        "name": rate_date,
                    })
                    if is_invoice_purchase_exchange_rate_installed:
                        rate_data["exchange_rate"] = exchange_rate
                    record = CurrencyRate.create(rate_data)
            else:
                rate_data.update({
                    "company_id": provider.company_id.id,
                    "currency_id": currency.id,
                    "name": rate_date,
                })
                if is_invoice_purchase_exchange_rate_installed:
                    rate_data["exchange_rate"] = exchange_rate
                record = CurrencyRate.create(rate_data)

        Currency = self.env["res.currency"]
        CurrencyRate = self.env["res.currency.rate"]
        is_scheduled = self.env.context.get("scheduled")
        for provider in self:
            try:
                data = provider._obtain_rates(
                    provider.company_id.currency_id.name,
                    provider.currency_ids.mapped("name"),
                    date_from,
                    date_to,
                )
                if data:
                    data = data.items()
            except BaseException as e:
                _logger.warning(
                    (
                        'Currency rate provider "{name}" failed to obtain data since'
                        " {date_from} until {date_to}"
                    ).format(
                        name=provider.name,
                        date_from=date_from,
                        date_to=date_to,
                    ),
                    exc_info=True,
                )
                provider.message_post(
                    subject=_("Currency Rate Provider Failure"),
                    body=_(
                        'Currency rate provider "%(name)s" failed to obtain data'
                        " since %(date_from)s until %(date_to)s:\n%(error)s"
                    )
                    % {
                        "name": provider.name,
                        "date_from": date_from,
                        "date_to": date_to,
                        "error": str(e) if e else _("N/A"),
                    },
                )
                continue

            if not data:
                continue
            if newest_only:
                data = [max(data, key=lambda x: fields.Date.from_string(x[0]))]

            newest_date = None
            for content_date, rates in data:
                rate_date = fields.Date.from_string(content_date)
                if not newest_date or rate_date > newest_date:
                    newest_date = rate_date
                for currency_name, rate_data in rates.items():
                    if currency_name == provider.company_id.currency_id.name:
                        continue

                    currency = Currency.search([("name", "=", currency_name)], limit=1)
                    if not currency:
                        raise UserError(
                            _("Unknown currency from %(provider)s: %(currency)s")
                            % {"provider": provider.name, "currency": currency_name}
                        )

                    for exchange_rate, rate in rate_data.items():
                        get_or_create_currency_rate(currency, exchange_rate, rate)

            if is_scheduled:
                provider._schedule_last_successful_run()
                provider._schedule_next_run()

    def _schedule_last_successful_run(self):
        self.last_successful_run = fields.Datetime.now()

    def _schedule_next_run(self):
        self.ensure_one()
        self.next_run = self.next_run + self._get_next_run_period()

    def _process_rate(self, currency, rate):
        self.ensure_one()

        Module = self.env["ir.module.module"]

        currency_rate_inverted = Module.sudo().search(
            [("name", "=", "currency_rate_inverted"), ("state", "=", "installed")],
            limit=1,
        )

        if isinstance(rate, dict):
            inverted = rate.get("inverted", None)
            direct = rate.get("direct", None)
            if inverted is None and direct is None:
                raise UserError(
                    _("Invalid rate from %(provider)s for %(currency)s: %(rate)s")
                    % {"provider": self.name, "currency": currency.name, "rate": rate}
                )
            elif inverted is None:
                inverted = 1 / direct
            elif direct is None:
                direct = 1 / inverted
        else:
            rate = float(rate)
            direct = rate
            inverted = 1 / rate

        value = direct
        if (
            currency_rate_inverted
            and currency.with_company(self.company_id).rate_inverted
        ):
            value = inverted

        return value

    def _get_next_run_period(self):
        self.ensure_one()
        if self.interval_type == "minutes":
            return relativedelta(minutes=self.interval_number)
        elif self.interval_type == "hours":
            return relativedelta(hours=self.interval_number)
        elif self.interval_type == "days":
            return relativedelta(days=self.interval_number)
        elif self.interval_type == "weeks":
            return relativedelta(weeks=self.interval_number)
        elif self.interval_type == "months":
            return relativedelta(months=self.interval_number)

    @api.model
    def _scheduled_update(self):
        _logger.info("Scheduled currency rates update...")

        now = fields.Datetime.context_timestamp(self, datetime.now())
        providers = self.search(
            [
                ("company_id.currency_rates_autoupdate", "=", True),
                ("active", "=", True),
                ("next_run", "<=", now),
            ]
        )
        if providers:
            _logger.info(
                "Scheduled currency rates update of: %s"
                % ", ".join(providers.mapped("name"))
            )
            for provider in providers.with_context(scheduled=True):
                date_from = (
                    provider.last_successful_run + relativedelta(seconds=1)
                    if provider.last_successful_run
                    else provider.next_run - provider._get_next_run_period()
                )
                newest_only = True
                date_to = provider.next_run
                provider._update(date_from, date_to, newest_only=newest_only)
        _logger.info("Scheduled currency rates update complete.")

    def _get_supported_currencies(self):
        # pragma: no cover
        self.ensure_one()
        return []

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        # pragma: no cover
        self.ensure_one()
        return {}

    @api.model
    def _is_invoice_purchase_exchange_rate_installed(self):
        return bool(
            self.env['ir.module.module']
            .sudo()
            .search([('name', '=', 'invoice_purchase_exchange_rate'), ('state', '=', 'installed')])
        )
