# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	has_analytic_distribution = fields.Boolean(string="Distribución Analítica",
		related="picking_type_id.has_analytic_distribution",store=True)

	########################################################################

	massive_analytic_distribution = fields.Json(
		'Distribución Analítica Masiva',
		compute="_compute_analytic_distribution", store=True, copy=True, readonly=False,
		precompute=True
	)

	# Json non stored to be able to search on analytic_distribution.
	analytic_distribution_search = fields.Json(store=False,search="_search_analytic_distribution")

	analytic_precision = fields.Integer(store=False,
		default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
	)

	def aplication_massive_analytic_distribution(self):
		if self.massive_analytic_distribution and self.move_ids_without_package:
			self.move_ids_without_package.write(
				{'analytic_distribution':self.massive_analytic_distribution})


	######################################################################
	def _compute_analytic_distribution(self):
		pass


	def _search_analytic_distribution(self, operator, value):
		if operator not in ['=', '!=', 'ilike', 'not ilike'] or not isinstance(value, (str, bool)):
			raise UserError(_('Operation not supported'))

		operator_name_search = '=' if operator in ('=', '!=') else 'ilike'
		account_ids = list(self.env['account.analytic.account']._name_search(name=value, operator=operator_name_search))

		query = f"""
			SELECT id
			FROM {self._table}
			WHERE analytic_distribution ?| array[%s]
		"""

		operator_inselect = 'inselect' if operator in ('=', 'ilike') else 'not inselect'
		return [('id', operator_inselect, (query, [[str(account_id) for account_id in account_ids]]))]




class StockMove(models.Model):
	_inherit = 'stock.move'

	analytic_distribution = fields.Json('Distribución Analítica',
		compute="_compute_analytic_distribution", store=True, copy=True, readonly=False,
		precompute=True)

	analytic_distribution_search = fields.Json(store=False, search="_search_analytic_distribution")

	analytic_precision = fields.Integer(store=False,
		default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),)

	######################################################################

	def _compute_analytic_distribution(self):
		pass


	def _search_analytic_distribution(self, operator, value):
		if operator not in ['=', '!=', 'ilike', 'not ilike'] or not isinstance(value, (str, bool)):
			raise UserError(_('Operation not supported'))

		operator_name_search = '=' if operator in ('=', '!=') else 'ilike'
		account_ids = list(self.env['account.analytic.account']._name_search(name=value, operator=operator_name_search))

		query = f"""
			SELECT id
			FROM {self._table}
			WHERE analytic_distribution ?| array[%s]
			"""
		operator_inselect = 'inselect' if operator in ('=', 'ilike') else 'not inselect'
		return [('id', operator_inselect, (query, [[str(account_id) for account_id in account_ids]]))]

	####################################################################################################

	"""def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description):
		self.ensure_one()

		debit_line_vals = {
			'name': description,
			'product_id': self.product_id.id,
			'quantity': qty,
			'product_uom_id': self.product_id.uom_id.id,
			'ref': description,
			'partner_id': partner_id,
			'balance': debit_value,
			'account_id': debit_account_id,
		}

		credit_line_vals = {
			'name': description,
			'product_id': self.product_id.id,
			'quantity': qty,
			'product_uom_id': self.product_id.uom_id.id,
			'ref': description,
			'partner_id': partner_id,
			'balance': -credit_value,
			'account_id': credit_account_id,
		}

		if self.product_id.categ_id and self.product_id.categ_id.property_stock_valuation_account_id and \
			debit_account_id != self.product_id.categ_id.property_stock_valuation_account_id.id:

			debit_line_vals['analytic_distribution'] = self.analytic_distribution or False

		elif self.product_id.categ_id and self.product_id.categ_id.property_stock_valuation_account_id and \
			credit_account_id != self.product_id.categ_id.property_stock_valuation_account_id.id:

			credit_line_vals['analytic_distribution'] = self.analytic_distribution or False


		rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
		if credit_value != debit_value:
			diff_amount = debit_value - credit_value
			price_diff_account = self.env.context.get('price_diff_account')
			if not price_diff_account:
				raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

			rslt['price_diff_line_vals'] = {
				'name': self.name,
				'product_id': self.product_id.id,
				'quantity': qty,
				'product_uom_id': self.product_id.uom_id.id,
				'balance': -diff_amount,
				'ref': description,
				'partner_id': partner_id,
				'account_id': price_diff_account.id,
			}
		return rslt """

	#######################################################################################

	def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description):

		result = super(StockMove,self)._generate_valuation_lines_data(
			partner_id, 
			qty, 
			debit_value, 
			credit_value, 
			debit_account_id, 
			credit_account_id, 
			svl_id, 
			description)
		

		debit_account_id = False
		credit_account_id = False

		if 'credit_line_vals' in result:
			if 'account_id' in result['credit_line_vals']:
				credit_account_id = result['credit_line_vals']['account_id']


		if 'debit_line_vals' in result:
			if 'account_id' in result['debit_line_vals']:
				debit_account_id = result['debit_line_vals']['account_id']


		if debit_account_id and self.product_id.categ_id and self.product_id.categ_id.property_stock_valuation_account_id and \
			debit_account_id != self.product_id.categ_id.property_stock_valuation_account_id.id:

			result['debit_line_vals']['analytic_distribution'] = self.analytic_distribution or False


		elif credit_account_id and self.product_id.categ_id and self.product_id.categ_id.property_stock_valuation_account_id and \
			credit_account_id != self.product_id.categ_id.property_stock_valuation_account_id.id:

			result['credit_line_vals']['analytic_distribution'] = self.analytic_distribution or False


		return result