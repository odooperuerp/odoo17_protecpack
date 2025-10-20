###############################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    origin_move_id = fields.Many2one(
        comodel_name="account.move", string="Origin entry", copy=False
    )
    origin_move_line_id = fields.Many2one(
        comodel_name="account.move.line", string="Origin move line", copy=False
    )
    target_move_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="origin_move_id",
        string="Target entries",
        copy=False,
    )
    target_move_count = fields.Integer(
        string="Target move count", compute="_compute_count_target_move"
    )

    def _compute_count_target_move(self):
        account_move = self.env["account.move"]
        for record in self:
            record.target_move_count = account_move.search_count(
                [("origin_move_id", "=", record.id)]
            )

    def generate_target_move_massive(self):
        for move in self:
            for line in move.line_ids.filtered(
                lambda r: r.account_id.target_account is True
            ):
                if not line.target_move_id:
                    move_data = {
                        "origin_move_id": move.id,
                        "origin_move_line_id": line.id,
                        "ref": line.name,
                        "date": line.date,
                        "journal_id": line.account_id.target_journal_id
                        and line.account_id.target_journal_id.id
                        or False,
                        "move_type": "entry",
                    }
                    target_move_id = self.env["account.move"].create(move_data)
                    line.target_move_id = target_move_id

                line_data = {
                    "origin_move_id": move.id,
                    "origin_move_line_id": line.id,
                    "name": line.name,
                    "ref": move.name,
                    "partner_id": line.partner_id and line.partner_id.id or False,
                    "currency_id": line.currency_id and line.currency_id.id or False,
                }
                debit_data = dict(line_data)
                credit_data = dict(line_data)

                if line.debit is not False:
                    debit_data.update(
                        account_id=line.account_id.debit_target_account_id.id,
                        debit=line.debit,
                        credit=False,
                        amount_currency=line.amount_currency,
                    )
                    credit_data.update(
                        account_id=line.account_id.credit_target_account_id.id,
                        debit=False,
                        credit=line.debit,
                        amount_currency=line.amount_currency * -1.0,
                    )
                else:
                    debit_data.update(
                        account_id=line.account_id.debit_target_account_id.id,
                        debit=False,
                        credit=line.credit,
                        amount_currency=line.amount_currency,
                    )
                    credit_data.update(
                        account_id=line.account_id.credit_target_account_id.id,
                        debit=line.credit,
                        credit=False,
                        amount_currency=line.amount_currency * -1.0,
                    )

                if not line.target_move_id.line_ids:
                    line.target_move_id.write(
                        {"line_ids": [(0, 0, debit_data), (0, 0, credit_data)]}
                    )
                else:
                    for line in line.target_move_id.line_ids:
                        if (
                            line.account_id.id
                            == line.account_id.debit_target_account_id.id
                        ):
                            line.write(debit_data)
                        if (
                            line.account_id.id
                            == line.account_id.credit_target_account_id.id
                        ):
                            line.write(credit_data)
                # Post Target move
                if line.target_move_id.state == "draft":
                    line.target_move_id.action_post()


    def action_post(self):
        res = super(AccountMove, self).action_post()
        for move in self:
            move.generate_target_move_massive()
            
            """for line in move.line_ids.filtered(
                lambda r: r.account_id.target_account is True
            ):
                if not line.target_move_id:
                    move_data = {
                        "origin_move_id": move.id,
                        "origin_move_line_id": line.id,
                        "ref": line.name,
                        "date": line.date,
                        "journal_id": line.account_id.target_journal_id
                        and line.account_id.target_journal_id.id
                        or False,
                        "move_type": "entry",
                    }
                    target_move_id = self.env["account.move"].create(move_data)
                    line.target_move_id = target_move_id

                line_data = {
                    "origin_move_id": move.id,
                    "origin_move_line_id": line.id,
                    "name": line.name,
                    "ref": move.name,
                    "partner_id": line.partner_id and line.partner_id.id or False,
                    "currency_id": line.currency_id and line.currency_id.id or False,
                }
                debit_data = dict(line_data)
                credit_data = dict(line_data)

                if line.debit is not False:
                    debit_data.update(
                        account_id=line.account_id.debit_target_account_id.id,
                        debit=line.debit,
                        credit=False,
                        amount_currency=line.amount_currency,
                    )
                    credit_data.update(
                        account_id=line.account_id.credit_target_account_id.id,
                        debit=False,
                        credit=line.debit,
                        amount_currency=line.amount_currency * -1.0,
                    )
                else:
                    debit_data.update(
                        account_id=line.account_id.debit_target_account_id.id,
                        debit=False,
                        credit=line.credit,
                        amount_currency=line.amount_currency,
                    )
                    credit_data.update(
                        account_id=line.account_id.credit_target_account_id.id,
                        debit=line.credit,
                        credit=False,
                        amount_currency=line.amount_currency * -1.0,
                    )

                if not line.target_move_id.line_ids:
                    line.target_move_id.write(
                        {"line_ids": [(0, 0, debit_data), (0, 0, credit_data)]}
                    )
                else:
                    for line in line.target_move_id.line_ids:
                        if (
                            line.account_id.id
                            == line.account_id.debit_target_account_id.id
                        ):
                            line.write(debit_data)
                        if (
                            line.account_id.id
                            == line.account_id.credit_target_account_id.id
                        ):
                            line.write(credit_data)
                # Post Target move
                if line.target_move_id.state == "draft":
                    line.target_move_id.action_post()"""

        return res


    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        for move in self:
            for target in move.target_move_ids:
                target.button_draft()
        return res


    def button_cancel(self):
        res = super(AccountMove, self).button_cancel()
        for move in self:
            for target in move.target_move_ids:
                target.button_cancel()
        return res


    def open_target_move_view(self):
        [action] = self.env.ref("account.action_move_line_form").read()
        ids = self.target_move_ids.ids
        action["domain"] = [("id", "in", ids)]
        action["name"] = "Target entries"
        return action


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    origin_move_id = fields.Many2one(
        comodel_name="account.move", string="Origin entry", copy=False
    )
    origin_move_line_id = fields.Many2one(
        comodel_name="account.move.line", string="Origin move line", ondelete="cascade"
    )
    target_move_id = fields.Many2one(
        comodel_name="account.move", string="Target entry", copy=False
    )
