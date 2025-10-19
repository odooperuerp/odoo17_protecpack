# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError
from odoo.tools import float_is_zero, float_compare

import logging
_logger = logging.getLogger(__name__)

class AccountDetraction(models.Model):
	_name = "account.detraction"
	_description = "Detracciones"
	_rec_name = "name_detraccion"

	@api.model
	def _operation_type(self):
		type = [('01', '01 - Venta de bienes o prestación de servicios'),
			('02', '02 - Retiro de bienes'),
			('03', '03 - Traslados que no son venta'),
			('04', '04 - Venta bolsa de productos'),
			('05', '05 - Venta de Bienes exonerados del IGV')]
		return type

	'''def _get_aml_for_amount_residual(self):
		#self.ensure_one()
		return self.sudo().move_id.line_ids.filtered(lambda l: l.account_id != self.destination_account_id)'''


	################################################################## compute_residual para casos donde detraction_journal_id.account_id == destination_account_id
	def _get_aml_for_amount_residual(self):
		""" Get the aml to consider to compute the amount residual of invoices """
		#self.ensure_one()
		aml_counterparts = self.sudo().move_id.line_ids.filtered(lambda l: l.account_id != self.destination_account_id) or \
			self.sudo().move_id.line_ids.filtered(lambda l: l.account_id == self.destination_account_id and l.balance>0)
		return aml_counterparts
	##################################################################


	@api.depends(
		'state', 'currency_id',
		'move_id.line_ids.amount_residual',
		'move_id.line_ids.currency_id')
	def _compute_residual(self):
		#self.ensure_one()
		for rec in self:
			residual = 0.0
			residual_company_signed = 0.0

			if rec.move_id:

				for line in rec._get_aml_for_amount_residual():

					residual_company_signed += line.amount_residual
					if line.currency_id == rec.currency_id:
						residual += line.amount_residual_currency if line.currency_id else line.amount_residual
					else:
						if line.currency_id:
							residual += line.currency_id._convert(line.amount_residual_currency, 
								rec.currency_id, line.company_id, line.date or fields.Date.today())

						else:
							residual += line.company_id.currency_id._convert(line.amount_residual, rec.currency_id, 
								line.company_id, line.date or fields.Date.today())

				rec.residual = abs(residual)
				digits = rec.currency_id.rounding
				if float_is_zero(rec.residual, precision_rounding=digits):
					rec.reconciled = True
				else:
					rec.reconciled = False


	journal_id = fields.Many2one('account.journal',
		string="Diario",
		required=True, domain=[('detraction', '=', True)])

	currency_id = fields.Many2one('res.currency', string='Moneda')

	company_currency_id = fields.Many2one('res.currency', string='Moneda compañia',
		required=True, default=lambda self: self.env.user.company_id.currency_id)
	
	company_id = fields.Many2one('res.company', related='journal_id.company_id', 
		string='Compañia', readonly=True)

	amount_real = fields.Monetary(string='Monto Detracción', required=True,
		currency_field='company_currency_id')

	amount = fields.Monetary(string='Cantidad a Pagar', required=True,
		currency_field='company_currency_id')
	
	nro_constancia = fields.Char(string="Nro. de Constancia",
		copy=False)
	
	fecha_pago = fields.Date(string="Fecha de pago", 
		copy=False)
	
	fecha_registro = fields.Date(string="Fecha de registro",
		required=True)

	
	detraccion_id = fields.Many2one('tipo.detraccion.line',
		string="Detracción", required=True)

	fecha_movimiento = fields.Date(string="Fecha de movimiento",
		required=True)

	communication = fields.Char(string='Concepto', required=True)

	origin_move_id = fields.Many2one('account.move', string="Documento",
		copy=False)

	partner_id = fields.Many2one('res.partner', related="origin_move_id.partner_id",
		string="Empresa")

	move_id = fields.Many2one('account.move', string="Asiento contable",
		copy=False,readonly=True)


	state = fields.Selection(selection=[
		('draft','Borrador'),('posted','Publicado'),('cancel','Cancelado')],
		readonly=True, string="Estado", default="draft")

	pay_state = fields.Selection(selection=[
		('to_pay', ' A Pagar'), ('paid','Pagado')], string="Estado de Pago", default='to_pay')


	destination_account_id = fields.Many2one('account.account',string="cuenta destino")


	residual = fields.Monetary(string="Importe adeudado",
		compute='_compute_residual', store=True, currency_field='company_currency_id')


	reconciled = fields.Boolean(string="reconciled", compute="_compute_residual", store=True)

	operation_type = fields.Selection(selection=_operation_type,
		string="Tipo de Operación", size=2, required=True,default='01')

	acc_number = fields.Char(string="Número cuenta detracción", required=True)

	name_detraccion = fields.Char(string="Nombre Detracción",
		compute="compute_campo_name_detraccion",store=True)
	##############################################################################

	@api.depends('origin_move_id','nro_constancia')
	def compute_campo_name_detraccion(self):
		for rec in self:
			name = "Detracción de %s %s" % (rec.origin_move_id and rec.origin_move_id.name or '', rec.nro_constancia or 'C/Pediente')
			rec.name_detraccion = name


	def name_get(self):
		result = []
		for inv in self:
			result.append((inv.id, "%s %s" % (inv.origin_move_id.name or '', inv.nro_constancia or 'C/Pediente')))
		return result


	@api.model
	def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
		args = args or []
		recs = []
		if name:
			recs = self._search([('nro_constancia', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid)
		if not recs:
			recs = self._search([('communication', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
		return self.browse(recs).name_get()

	#############################################################################

	@api.onchange('partner_id')
	def _change_partner_id(self):
		for rec in self:
			if rec.partner_id:
				bank = rec.partner_id.bank_ids.filtered(lambda b: b.detraction_bank)
				if bank:
					rec.acc_number = bank[0].acc_number.replace('-','')


	@api.onchange('origin_move_id')
	def _change_destination_account(self):
		for rec in self:
			if rec.origin_move_id:
				if rec.origin_move_id.move_type=='out_invoice':
					rec.destination_account_id = rec.origin_move_id.partner_id.property_account_receivable_id
				elif rec.origin_move_id.move_type=='in_invoice':
					rec.destination_account_id = rec.origin_move_id.partner_id.property_account_payable_id

				rec.amount_real = rec.origin_move_id.total_detraccion_contabilidad
				rec.amount = rec.origin_move_id.total_detraccion_contabilidad_manual
				rec.fecha_registro = rec.origin_move_id.date or fields.Date.context_today(rec)
				rec.fecha_movimiento = rec.origin_move_id.invoice_date


	
	def action_cancel_detraccion(self):
		for rec in self:
			if rec.move_id and rec.move_id.line_ids:

				move_id = rec.move_id

				if move_id.state=='posted':
					move_id.button_draft()

				self._cr.execute("DELETE FROM account_move_line WHERE move_id=%s"%(move_id.id))
				self._cr.execute("DELETE FROM account_move WHERE id=%s"%(move_id.id))

			rec.write({'state':'cancel'})

	
	def action_draft_detraccion(self):
		self.write({'state':'draft'})


	######################################
	def unlink (self):
		for line in self:
			if line.move_id and line.move_id.line_ids:

				line_move_id = line.move_id.id

				if line.move_id.state=='posted':
					line.move_id.button_draft()

				self._cr.execute("DELETE FROM account_move_line WHERE move_id=%s"%line_move_id)
				self._cr.execute("DELETE FROM account_move WHERE id=%s"%line_move_id)
			
			return super(AccountDetraction,line).unlink()
	######################################


	def action_validate_detraction(self):
		#self.ensure_one()
		if self.state != 'draft':
			raise UserError("Solo se puede publicar la detraccion en borrador")

		if self.origin_move_id.register_detraction_id:
			if self.origin_move_id.register_detraction_id.id != self.id:
				raise ValidationError("El registro no se puede procesar porque la factura tiene su detraccion")

		# Create the journal entry
		amount = self.amount * (self.origin_move_id.move_type in ('in_invoice', 'in_refund') and 1 or -1)
		if self.currency_id and self.currency_id != self.company_id.currency_id:
			amount = self.company_id.currency_id._convert(amount, self.currency_id, self.company_id,self.origin_move_id.invoice_date or self.fecha_pago)
		move = self._create_detraction_entry(amount)
		self.write({'state': 'posted','residual': amount})

		if self.origin_move_id.move_type in ['in_invoice', 'in_refund']:
			if not self.partner_id.bank_ids.filtered(lambda b: b.detraction_bank):
				self._create_acc_account()

			### Conciliando
			detraccion_aml_id = self.sudo().move_id.line_ids.filtered(
				lambda l: l.account_id == self.destination_account_id and l.balance>0)

			origin_aml_id = self.sudo().origin_move_id.line_ids.filtered(
				lambda l: l.account_id == self.destination_account_id and l.balance<0)

			(detraccion_aml_id + origin_aml_id).reconcile()

		return True


	def _create_acc_account(self):
		if self.acc_number:
			bank = self.env['res.partner.bank']
			bank.create({
				'acc_number': self.acc_number.strip(),
				'partner_id': self.partner_id.id,
				'acc_type': 'bank',
				'detraction_bank': True
				})


	def _get_move_vals(self, journal=None):
		journal = journal or self.journal_id
		move_vals = {
			'date': self.fecha_registro,
			'ref': self.communication or '' + self.nro_constancia or 'C/Pediente',
			'company_id': self.company_id.id,
			'journal_id': journal.id,
			'move_type':'entry',
		}
		return move_vals


	def _create_detraction_entry(self, amount):

		aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
		debit, credit, amount_currency, currency_id = aml_obj.with_context(
			date=self.origin_move_id.invoice_date or self.fecha_pago)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
		
		move = self.move_id
		
		if not self.move_id:
			move = self.env['account.move'].create(self._get_move_vals())
			self.move_id = move.id
		
		invoice_id = self.origin_move_id
		if not self.origin_move_id:
			raise UserError("Necesita una factura de origen")
		# Write line corresponding to invoice payment
		aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, invoice_id)
		aml_dict.update(account_id=self.destination_account_id.id)
		counterpart_aml = aml_obj.create(aml_dict)

		# Write counterpart lines
		liquit = False

		if not self.currency_id.is_zero(self.amount):
		
			#if not self.currency_id != self.company_id.currency_id:
			#	amount_currency = 0
		
			liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, invoice_id)
			liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
			liquit = aml_obj.create(liquidity_aml_dict)

		
		if move.state == 'draft':
			move.action_post()
		# conciliar el pago
		
		if invoice_id:
			invoice_id = invoice_id.with_context(detraction = True)
			if not invoice_id.register_detraction_id:
				invoice_id.register_detraction_id = self.id
			if invoice_id.state == 'draft':
				invoice_id.action_post()
			counterpart_aml.name = 'Detrac. %s constancia No%s' %(invoice_id.name, self.nro_constancia or 'C/Pediente')
			if liquit:
				liquit.name = 'Detrac. %s constancia No%s' %(invoice_id.name, self.nro_constancia or 'C/Pediente')
			move.ref = 'Detrac. %s, constancia No %s' %(invoice_id.name, self.nro_constancia or 'C/Pediente')
			# No se puede conciliar porque no aun no se a relizado el
			# invoice_id.register_payment(counterpart_aml)
		return move


	def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
		line_vals = {
			'partner_id': self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
			'move_id': move_id,
			'debit': debit,
			'credit': credit,
			'amount_currency': amount_currency or False,
			'journal_id': self.journal_id and self.journal_id.id or False,

			'detraction_id' : self.id,
			'nro_constancia' : self.nro_constancia,
			'name': invoice_id.name or self.communication or '/' + ' ' + (self.nro_constancia or 'C/Pediente'),
			'currency_id' : (self.currency_id != self.company_id.currency_id and self.currency_id.id) or self.company_id.currency_id.id,
		}
		'''if invoice_id:
			line_vals.update({
				'prefix_code': invoice_id.prefix_code,
				'invoice_number': invoice_id.invoice_number,
				'type_document_id':invoice_id.move_type_document_id.id or '',
				})'''

		return line_vals

	def _get_liquidity_move_line_vals(self, amount):
		account_id = (self.origin_move_id.move_type in ['in_invoice', 'in_refund'] and self.journal_id.detraction_account_id.id) or (self.origin_move_id.move_type in ['out_invoice', 'in_refund'] and self.journal_id.detraction_account_id.id)
		vals = {
			'account_id': account_id,
			'journal_id': self.journal_id and self.journal_id.id or False,
			'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or self.company_id.currency_id.id,
		}
		return vals
	


	@api.model
	def create(self, vals):
		res = super(AccountDetraction, self).create(vals)
		if vals.get('state') and vals.get('state') == 'draft':
			invoice = self.env['account.move'].browse(vals.get('origin_move_id'))
			invoice.write({'register_detraction_id':res.id})
		return res

	
	def action_detraction_paid(self):
		_logger.info('\n\nENTRE AL ACTION_DETRACTION_PAID !!!\n\n')
		detractions = self.filtered(lambda d: d.pay_state != 'paid')
		if detractions.filtered(lambda d: not d.reconciled):
			raise UserError(_("You cannot pay an detraction to pay which is partially paid. You neet to reconcile payment entries first."))
		for d in detractions:
			vals = {
				'pay_state': 'paid',
				}
			if not d.nro_constancia:
				move_line = d.move_id.line_ids.filtered(lambda aml: aml.account_id != d.destination_account_id)
				if move_line.full_reconcile_id:
					move_line_cpart = move_line.full_reconcile_id.reconciled_line_ids.filtered(lambda aml: aml.move_id != d.move_id)
					vals.update(
						nro_constancia = move_line_cpart[0].move_id.nro_constancia,
						fecha_pago = move_line_cpart[0].move_id.date)
					move_line.move_id.write({'nro_constancia': move_line_cpart[0].move_id.nro_constancia})
			d.write(vals)

	
	def action_detraction_re_open(self):
		if self.filtered(lambda d: d.pay_state != 'paid'):
			raise UserError(_('Detraction must be paid in order to set it register payment'))
		return self.write({'pay_state':'to_pay'})

	
	def _write(self, vals):
		pre_not_reconciled = self.filtered(lambda d: not d.reconciled)
		pre_reconciled = self - pre_not_reconciled
		res = super(AccountDetraction, self)._write(vals)
		reconciled = self.filtered(lambda d: d.reconciled)
		not_reconciled = self - reconciled
		(reconciled & pre_reconciled).filtered(lambda d: d.state == 'posted' and d.pay_state == 'to_pay').action_detraction_paid()

		(not_reconciled & pre_not_reconciled).filtered(lambda d: (d.state == 'posted' and d.pay_state == 'paid' and not d.origin_move_id) or (d.state == 'posted' and d.pay_state == 'paid' and d.origin_move_id.move_type in ['in_invoice','in_refund'])).action_detraction_re_open()
		return res