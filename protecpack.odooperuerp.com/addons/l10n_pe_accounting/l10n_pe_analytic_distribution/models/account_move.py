from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
	_inherit = "account.move"

	has_aml_distribution = fields.Boolean(string="Tiene Apuntes con Cuentas Destinables",
		compute="compute_campo_has_aml_distribution")

	has_distribution = fields.Boolean(string="Destinos Generados")

	distribution_move_id = fields.Many2one('account.move',string="Asiento de Destino",readonly=True)

	is_distribution_move = fields.Boolean(string="Es un Asiento de Destino",readonly=True)


	@api.depends(
		'distribution_move_id',
		'line_ids',
		'line_ids.account_id',
		'line_ids.analytic_distribution',
		'line_ids.account_id.has_distribution')
	def compute_campo_has_aml_distribution(self):
		for rec in self:

			rec.has_aml_distribution = False

			if (not rec.distribution_move_id) and rec.line_ids:
				line_has_distribution = rec.line_ids.filtered(
					lambda f:f.account_id and f.account_id.has_distribution and f.analytic_distribution)

				if len(line_has_distribution or ''):
					rec.has_aml_distribution = True

			else:
				rec.has_aml_distribution = False		



	def action_generated_destinos(self):
		for rec in self:

			if not (rec.company_id and rec.company_id.distribution_journal_id):
				raise UserError("Configure el Diario de Generación de Destinos en la sección de Configuraciones Contables !.")


			line_has_distribution = rec.line_ids.filtered(
				lambda f:f.account_id and f.account_id.has_distribution and f.analytic_distribution and (not f.has_distribution))

			if line_has_distribution:

				rec.distribution_move_id = self.env['account.move'].create({
					'move_type': 'entry',
					'date': rec.date,
					'ref': 'Asiento Destino de %s'%(rec.name or rec.ref or ''),
					'journal_id': rec.company_id and rec.company_id.distribution_journal_id and rec.company_id.distribution_journal_id.id or False,
					'is_distribution_move':True})

				for line in line_has_distribution:
					if (not line.has_distribution) and line.account_id.has_distribution and line.analytic_distribution:
						line._create_destinos_from_account_center(rec.distribution_move_id)

				rec.distribution_move_id.action_post()

				rec.has_distribution = True

			else:
				rec.has_distribution = False


	def deleted_am_distribution(self):
		for rec in self:
			if rec.distribution_move_id:

				rec.distribution_move_id.button_draft()
				rec.distribution_move_id.unlink()

				rec.line_ids.write({'has_distribution':False})
				rec.has_distribution = False

	###############################################################################

	def open_distribution_move_view(self):
		return {
			'name': 'Asiento Contable Destino de %s'%(self.name or self.ref or ''),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'account.move',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', [self.distribution_move_id.id] or [])]}


	def update_analytic_distribution(self):
		for rec in self:
			rec.line_ids.update_analytic_distribution()



class AccountMoveLine(models.Model):
	_inherit = "account.move.line"

	has_distribution = fields.Boolean(string="Tiene Destinos Generados")
	is_distribution = fields.Boolean(string="Es un movimiento de Destino")


	@api.model
	def _process_update_analytic_distribution(self, account_ids=[], code=False, not_journal_code=False):
		accounts = False
		account = self.env['account.account']
		if account_ids:
			accounts = account.browse(account_ids)
		if code:
			accounts = account.search([('code','=',str(code).strip())])
		if not accounts:
			accounts = self.env['account.account'].search([('has_distribution','=',True)])
		if accounts:
			domain = [('account_id','in',accounts.ids),('move_id.state','=','posted')]
			if not_journal_code:
				domain.append(('journal_id.code','!=',not_journal_code))
			move_lines = self.search(domain)
			# _logger.info('\n\n %r \n\n', move_lines)
			move_lines.update_analytic_distribution()


	def update_analytic_distribution(self):
		move_lines = self.filtered(lambda line: line.account_id.has_distribution)
		for ml in move_lines:
			ml.write({'analytic_tag_ids':[(6,0, ml.account_id.account_tag_id.ids + ml.analytic_tag_ids.ids)]  })
		# move_lines.create_analytic_lines()
		am = move_lines.mapped('move_id')
		for move in am:
			move.with_context(force_update_analytic=True).mapped('line_ids').create_analytic_lines()
		if am:
			self.invalidate_cache()


	
	def create_analytic_lines(self):
		""" Create analytic items upon validation of an account.move.line having an analytic account or an analytic distribution.
		"""
		account_ids = []
		line_ids = self.browse()
		for obj_line in self:
			values = []
			move_id = obj_line.move_id
			for tag in obj_line.analytic_tag_ids.filtered('active_analytic_distribution'):
				
				if obj_line.account_id.has_distribution:
					
					if tag.is_account_contra_unique:
						obj_line._create_contra_partida_unique(tag, values, account_ids)
				
				###################################
				monto = obj_line.balance
				monto_currency = obj_line.amount_currency
				len_distribution = len(tag.analytic_distribution_ids)
				currency = obj_line.currency_id or move_id.currency_id
				for distribution in tag.analytic_distribution_ids:
					vals_line = obj_line._prepare_analytic_distribution_line(distribution)

					self.env['account.analytic.line'].create(vals_line)
					amount_currency = -obj_line.amount_currency * distribution.percentage / 100.0
					if obj_line.account_id.has_distribution:
						len_distribution -= 1
						monto += currency.round(vals_line['amount'])
						vals_line['amount'] = currency.round(vals_line['amount'])

						amount_currency = currency.round(amount_currency)
						monto_currency += amount_currency
						if len_distribution == 0 and not float_is_zero(monto, precision_rounding=currency.rounding):
							# vals_line['amount'] += -monto if vals_line['amount'] < 0 else monto
							vals_line['amount'] += (monto *-1)

							amount_currency += -monto_currency if monto_currency < 0 else monto_currency
						obj_line._create_destino(vals_line, distribution, values, account_ids, amount_currency)
						
						if not tag.is_account_contra_unique:
							obj_line._create_contra_partida(vals_line, distribution, values, account_ids, amount_currency)
		##########################################################################################################
		
			line_ids |= move_id.mapped("line_ids").filtered(lambda line: line.account_id.id in account_ids)
			if values:
				self.env['account.move.line'].with_context(check_move_validity=False).create(values)
			#move_id._post_validate()
			if obj_line.analytic_account_id:
				vals_line = obj_line._prepare_analytic_line()[0]
				self.env['account.analytic.line'].create(vals_line)
		if line_ids:
			line_ids -= (line_ids - self)
			if self._context.get("force_update_analytic") and line_ids:
				self._cr.execute("""
					DELETE FROM account_move_line WHERE id IN %s
					""",([tuple(line_ids.ids)]))
			else:
				line_ids.unlink()




	def _create_contra_partida_unique(self, tags, values=[], account_ids=[]):

		if tags.is_account_contra_unique: 
			if not tags.account_contra_id:
				raise UserError("Registre cuenta de contrapartida")

		self.ensure_one()

		line_vals = {
			'account_id': tags.account_contra_id.id,
			'name': "[%s] %s" %(tags.name, self.name),
			'debit' : self.credit,
			'credit' : self.debit,
			}
		line_vals.update(self._get_values_ditribution())

		if self.currency_id and self.currency_id != self.company_currency_id:
			line_vals.update(
				amount_currency = self.amount_currency * -1,
				)
		account_ids.append(tags.account_contra_id.id)
		return values.append(line_vals)



	def _create_contra_partida(self, vals_dist, distribution, values=[], account_ids=[], amount_currency=False):
		self.ensure_one()
		if not (distribution.account_contra_id or distribution.account_id.account_contra_id):
			raise UserError("Registre Cuenta de Contrapartida")
		company_currency = self.company_currency_id
		diff_currency = self.currency_id != company_currency
		line_vals = {
			'account_id': (distribution.account_contra_id and distribution.account_contra_id.id) \
				or (distribution.account_id.account_contra_id and distribution.account_id.account_contra_id.id),
			'name': "[%s] %s" %(distribution.account_id and distribution.account_id.name or '', self.name),
			'credit' : abs(vals_dist['amount']) if self.debit > 0 else 0.0,
			'debit' : abs(vals_dist['amount']) if self.credit > 0 else 0.0,
			}

		line_vals.update(self._get_values_ditribution())

		if diff_currency and amount_currency:
			line_vals.update(
				amount_currency = amount_currency * 1
				)
		account_ids.append(
			(distribution.account_destino_id and distribution.account_destino_id.id) or (distribution.account_id.account_destino_id and distribution.account_id.account_destino_id.id))
		return values.append(line_vals)



	def _get_values_ditribution(self):
		values ={
			'tax_line_id': self.tax_line_id and self.tax_line_id.id or False,
			'partner_id': self.partner_id and self.partner_id.id or False,
			'analytic_account_id': self.analytic_account_id and self.analytic_account_id.id or False,
			'analytic_tag_ids': [(6,0,self.analytic_tag_ids.ids)],
			'move_id': self.move_id.id,
			'tax_exigible': self.tax_exigible,
			'company_id': self.company_id.id,
			'currency_id': self.currency_id and self.currency_id.id or False,
			'company_currency_id': self.company_currency_id.id,
			'product_id': self.product_id and self.product_id.id or False,
			'payment_id': self.payment_id and self.payment_id.id or False,
			'quantity': self.quantity,
			'ref': self.ref
		}
		if 'prefix_code' in self._fields:
			values.update(
				prefix_code = self.prefix_code,
				invoice_number = self.invoice_number,
				)
		if 'table10_id' in self._fields:
			values.update(
				table10_id = self.table10_id.id or False
				)
		return values


	def _create_destino(self, vals_dist, distribution, values=[], account_ids=[], amount_currency=False):
		self.ensure_one()
		if not distribution.account_destino_id:
			raise UserError("Registre cuenta de distribucion y/o destino")
		company_currency = self.company_currency_id
		diff_currency = self.currency_id != company_currency
		line_vals = {
			'account_id': distribution.account_destino_id.id,
			'name': "[%s] %s" %(distribution.account_id.name, self.name),
			'debit' : abs(vals_dist['amount']) if self.debit > 0 else 0.0,
			'credit' : abs(vals_dist['amount']) if self.credit > 0 else 0.0,
			}

		line_vals.update(self._get_values_ditribution())

		if diff_currency and amount_currency:
			line_vals.update(
				amount_currency = amount_currency * -1
				)
		account_ids.append(distribution.account_destino_id.id)
		return values.append(line_vals)


	##################################################################
	def _get_values_fields_destino_from_account_center(self,move_id):
		vals_distribution = {
			'partner_id': self.partner_id and self.partner_id.id or False,
			'move_id': move_id.id,
			'company_id': self.company_id.id,
			'currency_id': self.currency_id and self.currency_id.id or False,
			'company_currency_id': self.company_currency_id and self.company_currency_id.id or False,
			'product_id': self.product_id and self.product_id.id or False,
			'quantity': self.quantity or 0.00,
			'ref': self.ref or '',
		}

		return vals_distribution




	def _create_destinos_from_account_center(self,move_id):
		for rec in self:

			if move_id and (not rec.has_distribution) and rec.account_id.has_distribution and rec.analytic_distribution:

				for analytic_account_id, percentage in rec.analytic_distribution.items():
					analytic_account = self.env['account.analytic.account'].browse(int(analytic_account_id))

					if not analytic_account.account_destino_id or not analytic_account.account_contra_id:

						raise UserError("Configure la Cuenta de Destino y Contrapartida de la Cuenta Analítica %s !"%(
							analytic_account.name or ''))


				values = []

				for analytic_account_id, percentage in rec.analytic_distribution.items():

					analytic_account = self.env['account.analytic.account'].browse(int(analytic_account_id))

					vals_distribution = rec._get_values_fields_destino_from_account_center(move_id)

					extra_vals_distribution = {
						'account_id': analytic_account.account_destino_id.id,
						'name': "[%s] %s" %(analytic_account.name or '', rec.name or ''),
						'amount_currency': round(abs(rec.amount_currency)*float(percentage)*0.01 or 0.00,2),
						'debit' : round(abs(rec.debit-rec.credit)*float(percentage)*0.01 or 0.00,2),
						'credit' : 0.00,
						'is_distribution': True,
					}

					vals_distribution.update(extra_vals_distribution)
					
					values.append(vals_distribution)
					##############################################################################

					vals_contrapartida = rec._get_values_fields_destino_from_account_center(move_id)

					extra_vals_contrapartida = {
						'account_id': analytic_account.account_contra_id.id,
						'name': "[%s] %s" %(analytic_account.name or '', rec.name or ''),
						'amount_currency': (-1.00)*round(abs(rec.amount_currency)*float(percentage)*0.01 or 0.00,2),
						'credit' : round(abs(rec.debit-rec.credit)*float(percentage)*0.01 or 0.00,2),
						'debit': 0.00,
						'is_distribution': True,
					}


					vals_contrapartida.update(extra_vals_contrapartida)

					values.append(vals_contrapartida)

				####################################################################################

				if values:
					self.env['account.move.line'].with_context(check_move_validity=False).create(values)
					rec.has_distribution = True