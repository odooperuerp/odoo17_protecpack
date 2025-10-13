from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class AccountRegistroDUA(models.Model):
	_name = 'account.registro.dua'
	_description = "Registro de DUA"
	_rec_name = "name"


	state = fields.Selection(selection=[('draft', 'Borrador'), ('posted', 'Validado')],
		readonly=True,string="Estado", default="draft")


	company_id = fields.Many2one('res.company',
		string="Compañia",
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain=lambda self: [('id', 'in', [i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids])])


	name = fields.Char(string="Número DUA")

	company_currency_id=fields.Many2one('res.currency',string="Moneda de Compañia",
		compute="compute_campo_company_currency_id",store=True)


	template_dua_referencial_id = fields.Many2one('template.dua.informacion.referencial',
		string="Plantilla de Conceptos Referenciales")

	template_dua_anotable_id = fields.Many2one('template.dua.informacion.anotable',
		string="Plantilla de Conceptos Anotables")

	referencial_dua_line_ids = fields.One2many('account.dua.referencial.line','dua_id',
		string="Detalles de Conceptos Referenciales")
	
	anotable_dua_line_ids = fields.One2many('account.dua.anotable.line','dua_id',
		string="Detalles de Conceptos Anotables")
	
	#############################################################################################

	dua_date=fields.Date(string="Fecha de Pago DUA",default=datetime.now().date())
	
	partner_id = fields.Many2one('res.partner',string="Superintendencia de Aduanas")

	transient_expense_account_id = fields.Many2one('account.account',string="Cuenta Transitoria de Gasto-Base Imponible",
		required=True)

	dua_journal_id = fields.Many2one('account.journal',string="Diario de Registro")

	############################################################################################

	currency_id = fields.Many2one('res.currency',string="Moneda de Operación")
	
	amount_aduana_currency = fields.Monetary(string="Valor en Aduana",currency_field="currency_id",
		compute="compute_campo_amount_aduana_currency",store=True)

	amount_total = fields.Monetary(string="Monto Total a Pagar",
		currency_field="currency_id",
		compute="compute_campo_amount_total",store=True)

	
	amount_total_company_currency = fields.Monetary(string="Monto Total a Pagar en MN",
		currency_field="company_currency_id",
		compute="compute_campo_amount_total_company_currency",store=True)

	
	dua_move_id = fields.Many2one('account.move',string="Asiento Contable de DUA")

	##############################################################################

	def name_get(self):
		result = []
		for rec in self:
			result.append((rec.id,"Registro de DUA %s"%(rec.name or '')))
		return result


	@api.onchange('template_dua_referencial_id')
	def onchange_template_dua_referencial_id(self):
		for rec in self:

			if rec.template_dua_referencial_id:
				rec.referencial_dua_line_ids.unlink()

				registro=[]
				for line in rec.template_dua_referencial_id.conceptos_referencial_ids:
					registro.append((0,0,{
						'company_id':rec.company_id.id,
						'dua_id':rec.id,
						'name':line.name or '',
						'amount':0.00,
					}))

				rec.referencial_dua_line_ids = registro


	@api.onchange('template_dua_anotable_id')
	def onchange_template_dua_anotable_id(self):
		for rec in self:

			if rec.template_dua_anotable_id:
				rec.anotable_dua_line_ids.unlink()

				registro=[]
				for line in rec.template_dua_anotable_id.conceptos_anotable_ids:

					monto = 0.00

					if line.type_calculo == 'porcentaje':
						monto = (line.amount_porcentaje_monto or 0.00)*0.01*(rec.amount_aduana_currency or 0.00)
					elif line.type_calculo == 'monto':
						monto = line.amount_porcentaje_monto or 0.00

					registro.append((0,0,{
						'company_id':rec.company_id.id,
						'dua_id':rec.id,
						'product_id':line.product_id and line.product_id.id or False,
						'account_id':line.account_id and line.account_id.id or False,
						'tax_id':line.tax_id and line.tax_id.id or False,
						'type_concepto':line.type_concepto,
						'amount':monto,
					}))

				rec.anotable_dua_line_ids = registro


	@api.depends('company_id')
	def compute_campo_company_currency_id(self):
		for rec in self:
			rec.company_currency_id = False
			if rec.company_id:
				rec.company_currency_id = rec.company_id.currency_id or False


	@api.depends('referencial_dua_line_ids','referencial_dua_line_ids.amount')
	def compute_campo_amount_aduana_currency(self):
		for rec in self:
			rec.amount_aduana_currency = 0.00
			if rec.referencial_dua_line_ids:
				rec.amount_aduana_currency = sum(rec.referencial_dua_line_ids.mapped('amount'))


	@api.depends('anotable_dua_line_ids','anotable_dua_line_ids.amount')
	def compute_campo_amount_total(self):
		for rec in self:
			rec.amount_total = 0.00
			if rec.anotable_dua_line_ids:
				rec.amount_total = sum(rec.anotable_dua_line_ids.mapped('amount'))


	@api.depends('amount_total','dua_date')
	def compute_campo_amount_total_company_currency(self):
		for rec in self:

			rec.amount_total_company_currency = 0.00
			if rec.amount_total and rec.dua_date:
			
				rec.amount_total_company_currency = self.company_currency_id._convert(
					rec.amount_total,rec.currency_id,rec.company_id,rec.dua_date)

	##########################################################################################
	

	def generar_comprobante_DUA(self):

		if not self.rendicion_date or not self.journal_id or not self.ref:
			raise UserError(_('POR FAVOR LLENE LOS CAMPOS: FECHA RENDICIÓN, DIARIO Y REFERENCIA !'))
		### CREANDO EL ASIENTO DE LA RENDICIÓN
		self.rendicion_move_id = self.env['account.move'].create({
			'date': self.rendicion_date or '',
			'ref': self.ref or '',
			'journal_id': self.journal_id.id
		})

		new_account_move_line = self.env['account.move.line'].with_context(check_move_validity=False)


		sum_debit=0.00
		sum_credit=0.00
		sum_amount_currency=0.00


		## PRIMERO EXTORNANDO LAS CUENTAS X PAGAR DE DOCUMENTOS INVOICE

		pares_move_id=[]

		for line in self.rendicion_gastos_line_ids:

			line_payable_id = line.invoice_id.line_ids.filtered(lambda y:y.account_type == 'liability_payable')[0]


			diccionario_facturas = {

				'move_id':self.rendicion_move_id.id,
				'account_id':line_payable_id and line_payable_id.account_id and line_payable_id.account_id.id or False,
				'partner_id':line.partner_id.id or '',
				'journal_id':self.journal_id.id or '',
				'name':self.ref or '',
				'debit': abs(line.amount_total_rendir_company_currency) if line.balance_sign<0.00 else 0.00,
				'credit': abs(line.amount_total_rendir_company_currency) if line.balance_sign>=0.00 else 0.00,
			}
			

			if line.invoice_currency_id and line.invoice_currency_id != line.company_currency_id:
				diccionario_facturas['amount_currency'] = line.amount_total_rendir_currency*(line.balance_sign*(-1)) if line.invoice_currency_id and line.company_currency_id != line.invoice_currency_id else 0.00
				diccionario_facturas['currency_id'] = line.invoice_currency_id.id

			elif line.invoice_currency_id and line.invoice_currency_id == line.company_currency_id:
				diccionario_facturas['amount_currency'] = line.amount_total_rendir_company_currency*(line.balance_sign*(-1))
				diccionario_facturas['currency_id'] = line.company_currency_id.id


			move_line_id = new_account_move_line.create(diccionario_facturas)

			pares_move_id += [(line,move_line_id)]

			#################################################################################################################
			sum_debit += abs(line.amount_total_rendir_company_currency) if line.balance_sign<0.00 else 0.00
			sum_credit += abs(line.amount_total_rendir_company_currency) if line.balance_sign>=0.00 else 0.00

			if self.provision_account_move_line_id.currency_id and self.provision_account_move_line_id.currency_id != self.company_currency_id:

				if line.invoice_currency_id and line.company_currency_id != line.invoice_currency_id:
					sum_amount_currency += line.amount_total_rendir_currency*(line.balance_sign) or 0.00

				else:
					sum_amount_currency += self.company_currency_id._convert(
						abs(line.amount_total_rendir_company_currency),
						self.provision_account_move_line_id.currency_id,
						self.company_id or self.env['res.company']._company_default_get('account.invoice'),
						self.rendicion_date)*(line.balance_sign) or 0.00
			
		#############################################

		## CREANDO LOS APUNTES DE GASTOS SIN DOCUMENTO ##

		for line in self.rendicion_gastos_sindocumento_line_ids:

			diccionario_sin_documento = {
				'move_id':self.rendicion_move_id.id,
				'account_id':line.gasto_account_id.id,
				'partner_id':line.partner_id.id or '',
				'journal_id':self.journal_id.id or '',
				'name':self.ref or '',
				'debit': abs(line.amount_total_company_currency) if line.balance_sign>=0.00 else 0.00,
				'credit': abs(line.amount_total_company_currency) if line.balance_sign<0.00 else 0.00,
			}

			if line.currency_id and line.currency_id != line.company_currency_id:
				diccionario_sin_documento['amount_currency'] = line.amount_total if line.currency_id and line.company_currency_id != line.currency_id else 0.00
				diccionario_sin_documento['currency_id'] = line.currency_id.id

			elif line.currency_id and line.currency_id == line.company_currency_id:
				diccionario_sin_documento['amount_currency'] = line.amount_total_company_currency
				diccionario_sin_documento['currency_id'] = line.company_currency_id and line.company_currency_id.id or False

			move_line_id = new_account_move_line.create(diccionario_sin_documento)

			#################################################################################################################
			sum_debit += abs(line.amount_total_company_currency) if line.balance_sign>=0.00 else 0.00
			sum_credit += abs(line.amount_total_company_currency) if line.balance_sign<0.00 else 0.00

			if self.provision_account_move_line_id.currency_id and self.provision_account_move_line_id.currency_id != self.company_currency_id:

				if line.currency_id and line.company_currency_id != line.currency_id:
					sum_amount_currency += line.amount_total*(line.balance_sign) or 0.00

				else:
					sum_amount_currency += self.company_currency_id._convert(
						abs(line.amount_total_company_currency),
						self.provision_account_move_line_id.currency_id,
						self.company_id or self.env['res.company']._company_default_get('account.invoice'),
						self.rendicion_date)*(line.balance_sign) or 0.00

			#sum_amount_currency += line.amount_total if line.currency_id and line.company_currency_id != line.currency_id else 0.00
			#################################################################################################################


		## CREANDO EL APUNTE DE ENTREGA A RENDIR
		if self.return_diferencial:

			provision_move_line_id= None
			
			diccionario_rendicion = {
				'move_id':self.rendicion_move_id.id,
				'account_id':self.provision_account_id.id,
				'partner_id':self.partner_id.id or '',
				'journal_id':self.journal_id.id or '',
				'name':self.ref or '',
			}
			#############################################################
			credit_rendicion = 0.00

			if self.provision_account_move_line_id.currency_id and self.provision_account_move_line_id.currency_id != self.company_currency_id:

				credit_rendicion_currency = self.provision_account_move_line_id.currency_id._convert(
					abs(self.provision_account_move_line_id.amount_residual_currency) or 0.00,
					self.company_currency_id,
					self.company_id or self.env['res.company']._company_default_get('account.invoice'),
					self.rendicion_date)

				diccionario_rendicion['amount_currency'] = -abs(self.provision_account_move_line_id.amount_residual_currency) or 0.00
				diccionario_rendicion['currency_id'] = self.provision_account_move_line_id.currency_id and self.provision_account_move_line_id.currency_id.id
				diccionario_rendicion['debit'] = 0.00
				diccionario_rendicion['credit'] = credit_rendicion_currency
			else:
				credit_rendicion = abs(self.provision_account_move_line_id.amount_residual)

				diccionario_rendicion['amount_currency'] = -abs(self.provision_account_move_line_id.amount_residual) or 0.00
				diccionario_rendicion['currency_id'] = self.provision_account_move_line_id.currency_id and self.provision_account_move_line_id.currency_id.id

				diccionario_rendicion['debit'] = 0.00
				diccionario_rendicion['credit'] = abs(self.provision_account_move_line_id.amount_residual)
			#############################################################
			provision_move_line_id = new_account_move_line.create(diccionario_rendicion)

			if self.provision_account_move_line_id.currency_id and self.provision_account_move_line_id.currency_id != self.company_currency_id:
				saldo_residual_currency = abs(self.provision_account_move_line_id.amount_residual_currency) - sum_amount_currency
			
			saldo_residual = credit_rendicion - (sum_debit - sum_credit)

			
			## CREANDO APUNTE DE BANCO
			caja_banco_move_line_id = ''

			diccionario_devolucion = {}

			#############################################
			if self.provision_account_move_line_id.currency_id and self.provision_account_move_line_id.currency_id != self.company_currency_id:

				if not self.devolucion_reintegro_account_id:
					raise UserError(_("Especifique la Cuenta Contable de Devolución/Reintegro !"))

				if saldo_residual_currency or saldo_residual:

					diccionario_devolucion = {
						'move_id':self.rendicion_move_id.id,
						'account_id':self.devolucion_reintegro_account_id.id,
						'partner_id':(self.provision_payment_id and self.provision_payment_id.partner_id and self.provision_payment_id.partner_id.id) or \
							(self.provision_account_move_line_id.partner_id and self.provision_account_move_line_id.partner_id.id) or self.partner_id.id,
						'journal_id':self.journal_id.id or '',
						'name':self.ref or '',
						'debit': abs(saldo_residual) if saldo_residual >= 0.00 else 0.00,
						'credit': abs(saldo_residual) if saldo_residual < 0.00 else 0.00,
					}

					if self.devolucion_reintegro_account_id.currency_id and self.devolucion_reintegro_account_id.currency_id != self.company_currency_id:
						diccionario_devolucion['amount_currency'] = saldo_residual_currency
						diccionario_devolucion['currency_id'] = self.devolucion_reintegro_account_id.currency_id and self.devolucion_reintegro_account_id.currency_id.id or None


					caja_banco_move_line_id = new_account_move_line.create(diccionario_devolucion)

			else:
				if saldo_residual:

					if not self.devolucion_reintegro_account_id:
						raise UserError(_("Especifique la Cuenta Contable de Devolución/Reintegro !"))

					caja_banco_move_line_id = new_account_move_line.create({
						'move_id':self.rendicion_move_id.id,
						'account_id':self.devolucion_reintegro_account_id.id,
						'partner_id':(self.provision_payment_id and self.provision_payment_id.partner_id and self.provision_payment_id.partner_id.id) or \
							(self.provision_account_move_line_id.partner_id and self.provision_account_move_line_id.partner_id.id) or self.partner_id.id,
						'journal_id':self.journal_id.id or '',
						'name':self.ref or '',
						'debit': abs(saldo_residual) if saldo_residual >= 0.00 else 0.00,
						'credit': abs(saldo_residual) if saldo_residual < 0.00 else 0.00,
					})

					diccionario_devolucion['amount_currency'] = saldo_residual

					############## Me quede aqui !!!!!!!!!!!!!!!!!!
					diccionario_devolucion['currency_id'] = self.company_currency_id and self.company_currency_id.id


		else:
			provision_move_line_id=''

			diccionario ={
				'move_id':self.rendicion_move_id.id,
				'account_id':self.provision_account_id.id,
				'partner_id':self.partner_id.id or '',
				'journal_id':self.journal_id.id or '',
				'name':self.ref or '',
				'debit': abs(sum_debit-sum_credit) if (sum_debit-sum_credit)<0.00 else 0.00,
				'credit': abs(sum_debit-sum_credit) if (sum_debit-sum_credit)>=0.00 else 0.00,
			}

			_logger.info('\n\nDICCIONARIO\n\n')
			_logger.info(diccionario)

			if self.provision_currency_id and self.provision_currency_id != self.company_currency_id:
				
				amount_currency = self.provision_currency_id._convert(abs(sum_debit-sum_credit) or 0.00, self.company_currency_id,
					self.env['res.company']._company_default_get('account.invoice'), self.rendicion_date)

				diccionario['currency_id'] = self.provision_currency_id.id
				
				diccionario['amount_currency'] = amount_currency if (sum_debit-sum_credit)<0.00 else -amount_currency

			provision_move_line_id = new_account_move_line.create(diccionario)

		#######################################################

		self.rendicion_move_id.action_post()

		### CONCILIANDO LINEAS DE FACTURAS DE GASTO !!
		for i in pares_move_id:
			(i[0].invoice_aml_id + i[1]).reconcile()

		_logger.info('\n\nCONCILIE FACTURAS\n\n')

		### CONCILIANDO APUNTES DE PROVISION DE GASTOS !!
		(provision_move_line_id + self.provision_account_move_line_id).reconcile()

		self.state='posted'

	#####################################

	def button_view_move_id(self):
		if self.state == 'posted':
			return {
				'name': 'Asiento Contable Registro de DUA',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'account.move',
				'view_id': False,
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', [self.rendicion_move_id.id] or [])],
				'context': {
					'journal_id': self.journal_id.id,
				}
			}