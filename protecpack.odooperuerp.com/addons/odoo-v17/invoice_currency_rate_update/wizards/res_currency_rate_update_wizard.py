from odoo import fields, models


class ResCurrencyRateUpdateWizard(models.TransientModel):
    _name = "res.currency.rate.update.wizard"
    _description = "Manually Update Exchange Rate Wizard"

    date_from = fields.Datetime(
        string="Start Date", required=True, default=fields.Datetime.now
    )
    date_to = fields.Datetime(
        string="End Date", required=True, default=fields.Datetime.now
    )
    provider_ids = fields.Many2many(
        string="Providers",
        comodel_name="res.currency.rate.provider",
        column1="wizard_id",
        column2="provider_id",
    )

    def action_update(self):
        self.ensure_one()

        self.provider_ids._update(self.date_from, self.date_to)

        return {"type": "ir.actions.act_window_close"}
