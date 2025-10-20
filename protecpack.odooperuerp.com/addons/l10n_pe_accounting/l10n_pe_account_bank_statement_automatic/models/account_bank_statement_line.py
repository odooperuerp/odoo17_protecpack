from odoo import fields,models,api

class AccountBankStatementLine(models.Model):
	_inherit = "account.bank.statement.line"


	operation_number = fields.Char(string="Número de operación")

	def action_account_bank_statement_line_automatic(self):
		action = self.env['ir.actions.act_window']._for_xml_id(
			'l10n_pe_account_bank_statement_automatic.account_bank_statement_line_wizard_action')
		ctx = dict(self.env.context)
		ctx.pop('active_id', None)
		ctx['active_ids'] = self.ids
		ctx['active_model'] = 'account.bank.statement.line'
		action['context'] = ctx
		return action


	def button_view_account_move_line(self):

		return {
			'name': 'Apunte Contable',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'account.move.line',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', self.mapped('move_line_id').ids or [])],
		}

###############################################################################

