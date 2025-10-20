from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class AccountMoveCompensation(models.Model):
	_name = 'account.move.compensation'
	_description = "Registro de Compensación de Cuentas por Cobrar y Pagar"
	_rec_name = "compensation_move_id"


	state = fields.Selection(selection=[('open', 'Abierto'), ('send', 'Compensado')],
		readonly=True, string="Estado", default="open")

	company_id = fields.Many2one('res.company',
		string="Compañia",
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain=lambda self: [('id', 'in', [i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids])],
		compute="compute_campo_company_id",store=True)

	company_currency_id=fields.Many2one('res.currency',string="Moneda de Compañia",
		compute="compute_campo_company_currency_id")
	
	##########################################################################################################################
	account_receivable_line_ids = fields.One2many('account.move.compensation.receivable.line',
		'account_move_compensation_receivable_id',string="Documentos por Cobrar a Compensar")

	account_payable_line_ids = fields.One2many('account.move.compensation.payable.line',
		'account_move_compensation_payable_id',string="Documentos por Pagar a Compensar")
	##########################################################################################################################
	
	compensation_type = fields.Selection(selection=[('1','Compensación Total'),('2','Compensación Parcial')],
		string="Tipo de Compensación",default='2')
	#############################################################################################

	
	compensation_date = fields.Date(string="Fecha de Compensación",
		default = datetime.now().date())
	
	partner_id = fields.Many2one('res.partner',string="Cliente/Proveedor")

	compensation_dif_account_id = fields.Many2one('account.account',string="Cuenta de Compensación")

	###########################################################################################
	amount_compensation_receivable_company_currency = fields.Monetary(string="Monto Total Compensado por Cobrar MN",
		currency_field="company_currency_id",
		compute="compute_campo_amount_compensation_receivable_company_currency",store=True)

	amount_compensation_payable_company_currency = fields.Monetary(string="Monto Total Compensado por Pagar MN",
		currency_field="company_currency_id",
		compute="compute_campo_amount_compensation_payable_company_currency",store=True)

	amount_receivable_payable_diferencial_company_currency = fields.Float(string="Diferencia en Montos de Compensación",
		currency_field="company_currency_id",
		compute="compute_campo_amount_receivable_payable_diferencial_company_currency",store=True)

	###########################################################################################
	
	#### campos del asiento de compensación ####
	compensation_move_id = fields.Many2one('account.move',string="Asiento Contable de Compensación")
	journal_id = fields.Many2one('account.journal',string="Diario")#,domain="[('type', 'in',['cash','bank'])]")
	ref = fields.Char(string="Referencia")
	############################################################################


	def name_get(self):
		result = []
		for rec in self:
			result.append((rec.id,"Compensación %s"%(rec.compensation_move_id.name or '')))
		return result

	################################

	@api.depends('company_id')
	def compute_campo_company_id(self):
		for rec in self:
			rec.company_id = self.env['res.company']._company_default_get('account.invoice')


	@api.depends('company_id')
	def compute_campo_company_currency_id(self):
		for rec in self:
			if rec.company_id:
				rec.company_currency_id = rec.company_id.currency_id or False
			else:
				rec.company_currency_id = False


	#######################################################################################################

	@api.depends('account_receivable_line_ids','account_receivable_line_ids.amount_compensation')
	def compute_campo_amount_compensation_receivable_company_currency(self):
		for rec in self:
			if rec.account_receivable_line_ids:
				rec.amount_compensation_receivable_company_currency = \
					sum(rec.account_receivable_line_ids.mapped('amount_compensation_company_currency'))




	@api.depends('account_payable_line_ids','account_payable_line_ids.amount_compensation')
	def compute_campo_amount_compensation_payable_company_currency(self):
		for rec in self:
			if rec.account_payable_line_ids:
				rec.amount_compensation_payable_company_currency = \
					sum(rec.account_payable_line_ids.mapped('amount_compensation_company_currency'))




	@api.depends('amount_compensation_payable_company_currency','amount_compensation_receivable_company_currency')
	def compute_campo_amount_receivable_payable_diferencial_company_currency(self):
		for rec in self:
			rec.amount_receivable_payable_diferencial_company_currency = rec.amount_compensation_receivable_company_currency - \
				rec.amount_compensation_payable_company_currency
	##########################################################################################################


	def compensar_cuentas_cobrar_pagar(self):
		if not self.compensation_date or not self.journal_id or not self.ref:
			raise UserError(_('POR FAVOR LLENE LOS CAMPOS: FECHA DE REGISTRO DE COMPENSACIÓN, DIARIO Y REFERENCIA !!'))

		if self.compensation_type=='2' and abs(self.amount_receivable_payable_diferencial_company_currency) > 0.00:
			raise UserError(_('PARA ESTE TIPO DE COMPENSACIÓN LOS MONTOS DE COMPENSACIÓN DE LAS CUENTAS POR COBRAR Y PAGAR DEBEN COINCIDIR !!'))

		if self.compensation_type=='1' and not self.compensation_dif_account_id:
			raise UserError(_('PARA ESTE TIPO DE COMPENSACIÓN DEBE ESTABLECER UNA CUENTA PARA LA DIFERENCIA ENTRE LOS MONTOS DE COMPENSACIÓN POR COBRAR Y PAGAR !!'))



		self.compensation_move_id = self.env['account.move'].create({
			'date': self.compensation_date or '',
			'ref': self.ref or '',
			'journal_id': self.journal_id.id})

		new_account_move_line = self.env['account.move.line'].with_context(check_move_validity=False)

		sum_debit=0.00
		sum_credit=0.00
		sum_amount_currency=0.00
		
		## EXTORNANDO LAS CUENTAS X PAGAR DE DOCUMENTOS

		pares_move_id=[]
		for line in self.account_payable_line_ids:
			move_line_id = new_account_move_line.create({
				'move_id':self.compensation_move_id.id,
				'account_id':line.invoice_aml_id.account_id.id,
				'partner_id':self.partner_id.id or '',
				'journal_id':self.journal_id.id or '',
				'l10n_latam_document_type_id':line.tipo_doc_id and line.tipo_doc_id.id or False,
				'l10n_pe_prefix_code':line.prefix_code or '',
				'l10n_pe_invoice_number':line.invoice_number or '',
				'name':self.ref or '',
				'amount_currency':line.amount_compensation if line.invoice_currency_id and line.company_currency_id != line.invoice_currency_id else round(abs(line.amount_compensation_company_currency),2),
				'debit': round(abs(line.amount_compensation_company_currency),2),
				'credit': 0.00,
				'currency_id':line.invoice_currency_id.id if line.invoice_currency_id and line.company_currency_id != line.invoice_currency_id else self.company_id.currency_id.id,
			})
			pares_move_id += [(line,move_line_id)]

			#################################################################################################################
			sum_debit += round(abs(line.amount_compensation_company_currency),2)
			sum_credit += 0.00
			sum_amount_currency += line.amount_compensation if line.invoice_currency_id and line.company_currency_id != line.invoice_currency_id else 0.00
			#################################################################################################################

		## EXTORNANDO LAS CUENTAS X COBRAR DE DOCUMENTOS

		pares_2_move_id=[]
		for line in self.account_receivable_line_ids:
			move_line_id = new_account_move_line.create({
				'move_id':self.compensation_move_id.id,
				'account_id':line.invoice_aml_id.account_id.id,
				'partner_id':self.partner_id.id or '',
				'journal_id':self.journal_id.id or '',
				'l10n_latam_document_type_id':line.tipo_doc_id and line.tipo_doc_id.id or False,
				'l10n_pe_prefix_code':line.prefix_code or '',
				'l10n_pe_invoice_number':line.invoice_number or '',
				'name':self.ref or '',
				'amount_currency':(-1.00)*line.amount_compensation if line.invoice_currency_id and line.company_currency_id != line.invoice_currency_id else (-1.00)*round(abs(line.amount_compensation_company_currency),2),
				'debit': 0.00,
				'credit': round(abs(line.amount_compensation_company_currency),2),
				'currency_id':line.invoice_currency_id.id if line.invoice_currency_id and line.company_currency_id != line.invoice_currency_id else self.company_id.currency_id.id,
			})
			pares_2_move_id += [(line,move_line_id)]

			#################################################################################################################
			sum_debit += 0.00
			sum_credit += round(abs(line.amount_compensation_company_currency),2)
			sum_amount_currency += (-1.00)*line.amount_compensation if line.invoice_currency_id and line.company_currency_id != line.invoice_currency_id else 0.00
			#################################################################################################################


		if self.compensation_type=='1':

			compensation_move_line_id = ''

			dict_aml_id = {
				'move_id':self.compensation_move_id.id,
				'account_id':self.compensation_dif_account_id.id,
				'partner_id':self.partner_id.id or '',
				'journal_id':self.journal_id.id or '',
				'name':self.ref or '',
				}

			if self.amount_receivable_payable_diferencial_company_currency<0.00:
				
				if self.compensation_dif_account_id.currency_id and \
					self.compensation_dif_account_id.currency_id != self.company_currency_id:
					
					dict_aml_id['currency_id'] = self.compensation_dif_account_id.currency_id.id or False
					
					dict_aml_id['amount_currency'] = (-1.00)*self.company_currency_id._convert(
						abs(self.amount_receivable_payable_diferencial_company_currency or 0.00),
						self.compensation_dif_account_id.currency_id or False,
						self.company_id or False,
						self.compensation_date or False)

					dict_aml_id['debit'] = 0.00
					dict_aml_id['credit'] = round(abs(self.amount_receivable_payable_diferencial_company_currency or 0.00),2)

				
				else:
				
					dict_aml_id['currency_id'] = self.company_id.currency_id.id
					dict_aml_id['amount_currency'] = (-1.00)*abs(self.amount_receivable_payable_diferencial_company_currency or 0.00)
					dict_aml_id['debit'] = 0.00
					dict_aml_id['credit'] = round(abs(self.amount_receivable_payable_diferencial_company_currency or 0.00),2)


			elif self.amount_receivable_payable_diferencial_company_currency>0.00:

				if self.compensation_dif_account_id.currency_id and \
					self.compensation_dif_account_id.currency_id != self.company_currency_id:
					
					dict_aml_id['currency_id'] = self.compensation_dif_account_id.currency_id.id or self.company_id.currency_id.id
					
					dict_aml_id['amount_currency'] = (1.00)*self.company_currency_id._convert(
						abs(self.amount_receivable_payable_diferencial_company_currency or 0.00),
						self.compensation_dif_account_id.currency_id or False,
						self.company_id or False,
						self.compensation_date or False)

					dict_aml_id['debit'] = round(abs(self.amount_receivable_payable_diferencial_company_currency or 0.00),2)
					dict_aml_id['credit'] = 0.00

				
				else:
				
					dict_aml_id['currency_id'] = self.company_id.currency_id.id
					dict_aml_id['amount_currency'] = round(abs(self.amount_receivable_payable_diferencial_company_currency or 0.00),2)
					dict_aml_id['debit'] = round(abs(self.amount_receivable_payable_diferencial_company_currency or 0.00),2)
					dict_aml_id['credit'] = 0.00
			
			########################################################################################
			compensation_move_line_id = new_account_move_line.create(dict_aml_id)

			_logger.info('\n\nAPUNTE CONTABLE COMPENSACION\n')
			_logger.info(dict_aml_id)	
			########################################################################################


		_logger.info('\n\nASIENTO CONTABLE COMPENSACION\n')
		_logger.info(self.compensation_move_id)	

		_logger.info(self.compensation_move_id.line_ids)


		_logger.info(sum(self.compensation_move_id.line_ids.mapped('debit')))
		_logger.info(sum(self.compensation_move_id.line_ids.mapped('credit')))


		self.compensation_move_id.action_post()

		### CONCILIANDO LINEAS DE FACTURAS DE GASTO !!
		for i in pares_move_id:
			(i[0].invoice_aml_id + i[1]).reconcile()

		for i in pares_2_move_id:
			(i[0].invoice_aml_id + i[1]).reconcile()


		self.state='send'

	#####################################


	def button_view_move_id(self):
		if self.state == 'send':
			return {
				'name': 'Asiento Contable de Compensación',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'account.move',
				'view_id': False,
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', [self.compensation_move_id.id] or [])],
			}



	def button_view_aml_receivable_ids(self):
		if self.state == 'send':
			aml_receivable_ids = self.account_receivable_line_ids.mapped('invoice_aml_id.id')
			view = self.env.ref('account.view_move_line_tree')

			if aml_receivable_ids and view:
				return {
					'name': 'Movimientos de Cuentas por Cobrar Compensados',
					'view_type': 'form',
					'view_mode': 'tree,form',
					'res_model': 'account.move.line',
					'view_id': view.id,
					'views': [(view.id,'tree')],
					'type': 'ir.actions.act_window',
					'domain': [('id', 'in', list(aml_receivable_ids) or [])],
				}



	def button_view_aml_payable_ids(self):
		if self.state == 'send':
			aml_payable_ids = self.account_payable_line_ids.mapped('invoice_aml_id.id')
			view = self.env.ref('account.view_move_line_tree')

			if aml_payable_ids and view:
				return {
					'name': 'Movimientos de Cuentas por Pagar Compensados',
					'view_type': 'form',
					'view_mode': 'tree,form',
					'res_model': 'account.move.line',
					'view_id': view.id,
					'views': [(view.id,'tree')],
					'type': 'ir.actions.act_window',
					'domain': [('id', 'in', list(aml_payable_ids) or [])],
				}

	#####################################################################################
	@api.constrains('account_receivable_line_ids','account_receivable_line_ids.amount_compensation',)
	def _check_positive_amount_compensation_receivable(self):
		for rec in self:
			if rec.account_receivable_line_ids:
				for record in rec.account_receivable_line_ids:
					if record.amount_compensation<= 0.00:
						raise UserError("El Monto a compensar de cada línea debe ser mayor a 0.00 !!")


	@api.constrains('account_payable_line_ids','account_payable_line_ids.amount_compensation',)
	def _check_positive_amount_compensation_payable(self):
		for rec in self:
			if rec.account_payable_line_ids:
				for record in rec.account_payable_line_ids:
					if record.amount_compensation<= 0.00:
						raise UserError("El Monto a compensar de cada línea debe ser mayor a 0.00 !!")

	#####################################################################################

	@api.constrains('account_receivable_line_ids','account_receivable_line_ids.amount_compensation',
		'account_receivable_line_ids.amount_residual_currency','account_receivable_line_ids.amount_residual_company_currency',
		'account_receivable_line_ids.amount_compensation_company_currency','account_receivable_line_ids.invoice_currency_id',
		'account_receivable_line_ids.company_currency_id')
	def _check_maximun_amount_compensation_receivable(self):
		for rec in self:
			if rec.account_receivable_line_ids:
				for record in rec.account_receivable_line_ids:

					if record.invoice_currency_id and record.invoice_currency_id != record.company_currency_id:
						if record.amount_compensation > record.amount_residual_currency:
							raise UserError("El Monto a compensar de cada línea debe ser menor o igual al saldo residual !!")

					else:
						if record.amount_compensation > record.amount_residual_company_currency:
							raise UserError("El Monto a compensar de cada línea debe ser menor o igual al saldo residual !!")



	@api.constrains('account_payable_line_ids','account_payable_line_ids.amount_compensation',
		'account_payable_line_ids.amount_residual_currency','account_payable_line_ids.amount_residual_company_currency',
		'account_payable_line_ids.amount_compensation_company_currency','account_payable_line_ids.invoice_currency_id',
		'account_payable_line_ids.company_currency_id')
	def _check_maximun_amount_compensation_payable(self):
		for rec in self:
			if rec.account_payable_line_ids:
				for record in rec.account_payable_line_ids:

					if record.invoice_currency_id and record.invoice_currency_id != record.company_currency_id:
						if record.amount_compensation > record.amount_residual_currency:
							raise UserError("El Monto a compensar de cada línea debe ser menor o igual al saldo residual !!")

					else:
						if record.amount_compensation > record.amount_residual_company_currency:
							raise UserError("El Monto a compensar de cada línea debe ser menor o igual al saldo residual !!")