from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class AccountRendicionGastos(models.Model):
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_name = 'account.rendicion.gastos'
	_description = "Registro de Rendición de Gastos"
	_rec_name = "name"


	state = fields.Selection(selection=[('open', 'Abierto'), ('send', 'Rendido')],
		readonly=True,string="Estado", default="open")


	company_id = fields.Many2one('res.company',
		string="Compañia",
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain=lambda self: [('id', 'in', [i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids])],
		compute="compute_campo_company_id",store=True)


	name = fields.Char(string="Nombre",compute="compute_campo_name",store=True)

	company_currency_id=fields.Many2one('res.currency',string="Moneda de Compañia",
		compute="compute_campo_company_currency_id",store=True)
	
	
	rendicion_gastos_line_ids = fields.One2many('account.rendicion.gastos.line','rendicion_gastos_id',
		string="Documentos de Gastos a Rendir")
	
	
	rendicion_gastos_sindocumento_line_ids = fields.One2many('account.rendicion.gastos.sindocumento.line',
		'rendicion_gastos_id',
		string="Gastos sin Documento a Rendir")
	
	#############################################################################################
	
	rendicion_type = fields.Selection(selection=[('1','Gasto General'),('2','Devolución'),('3','Reintegro')],
		string="Tipo de gasto")

	return_diferencial = fields.Boolean(string="Generar Devolución/Reintegro Automáticamente",default=False)

	devolucion_reintegro_account_id = fields.Many2one('account.account',string="Cuenta de Devolución/Reintegro")
	
	#############################################################################################
	
	rendicion_date=fields.Date(string="Fecha de Rendición",default=datetime.now().date())
	
	partner_id = fields.Many2one('res.partner',string="Empleado/Socio")

	provision_payment_id=fields.Many2one('account.payment',string="Provisión de la Entrega a Rendir", 
		domain=[('payment_type', 'in',['outbound'])])

	provision_account_move_line_id = fields.Many2one('account.move.line',
		string="Movimiento de la Provisión",required=True)

	provision_account_id = fields.Many2one('account.account',string="Cuenta de Entrega a Rendir",
		required=True,domain="[('reconcile', 'in',[True])]")

	############################################################################################

	provision_currency_id = fields.Many2one('res.currency',string="Moneda de Provisión",
		compute="compute_campo_provision_currency_id",store=True)
	
	amount_provision_currency = fields.Monetary(string="Monto de Provisión",currency_field="provision_currency_id",
		compute="compute_campo_amount_provision_currency",store=True)

	amount_provision_company_currency = fields.Monetary(string="Monto de Provisión en MN",
		currency_field="company_currency_id",
		compute="compute_campo_amount_provision_company_currency",store=True)

	amount_residual_provision = fields.Monetary(string="Saldo de Provisión",currency_field="provision_currency_id",
		compute="compute_campo_amount_residual_provision",store=True)
	
	###########################################################################################
	amount_rendido_company_currency = fields.Monetary(string="Gastos Rendidos con Documentos en MN",
		currency_field="company_currency_id",
		compute="compute_campo_amount_rendido_company_currency",store=True)

	
	amount_rendido_sin_documentos_company_currency = fields.Monetary(string="Gastos Rendidos sin Documentos en MN",
		currency_field="company_currency_id",
		compute="compute_campo_amount_rendido_sin_documentos_company_currency",store=True)

	
	amount_rendido_total_company_currency=fields.Monetary(string="Monto Rendido Total en MN",
		currency_field="company_currency_id",
		compute="compute_campo_amount_rendido_total_company_currency",store=True)


	amount_diferencia_total_company_currency=fields.Monetary(string="Diferencia en MN (Provisión - Rendido)",
		currency_field="company_currency_id",
		compute="compute_campo_amount_diferencia_total_company_currency",store=True)
	###########################################################################################
	
	#### campos del asiento de rendicion de gastos
	
	rendicion_move_id = fields.Many2one('account.move',string="Asiento Contable de Rendición")
	journal_id = fields.Many2one('account.journal',string="Diario")
	ref = fields.Char(string="Referencia")
	##############################################################################

	## restricciones para evitar el múltiple ingreso del mismo documento a rendir ##
	@api.constrains('rendicion_gastos_line_ids','rendicion_gastos_line_ids.invoice_aml_id')
	def _check_campo(self):
		for record in self:
			if record.rendicion_gastos_line_ids:
				list_aml_id = [i.invoice_aml_id for i in record.rendicion_gastos_line_ids]
				if list_aml_id:
					if len(list_aml_id) != len(set(list_aml_id)):
						raise models.ValidationError('Solo se permite una linea de rendición por documento !\n.Elimine las lineas con documentos duplicados')



	@api.onchange('rendicion_gastos_line_ids','rendicion_gastos_line_ids.invoice_aml_id')
	def validate_no_duplicate_documents(self):
		for record in self:
			if record.rendicion_gastos_line_ids:
				list_aml_id = [i.invoice_aml_id for i in record.rendicion_gastos_line_ids]
				if list_aml_id:
					if len(list_aml_id) != len(set(list_aml_id)):
						raise models.ValidationError('El documento ingresado ya existe en otra linea para la presente hoja de rendición !')
	##############################################################################

	@api.depends('provision_payment_id','provision_payment_id.name')
	def compute_campo_name(self):
		for rec in self:
			if rec.provision_payment_id:
				rec.name = "Rendición de Gastos %s"%(rec.provision_payment_id.name or rec.rendicion_move_id.name or '')
			else:
				rec.name = "Rendición de Gastos Nueva"


	def name_get(self):
		result = []
		for rec in self:
			result.append((rec.id,"Rendición de Gastos %s"%(rec.provision_payment_id.name or rec.rendicion_move_id.name or '')))
		return result


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


	#################################################################
	@api.onchange('partner_id')
	def set_domain_for_provision_payment_id(self):
		if self.partner_id:
			records = []
			records = self.env['account.payment'].search(
				[('payment_type','in',['outbound']),('partner_id','=',self.partner_id.id)])

			res = {}
			res['domain'] = {'provision_payment_id': [('id', 'in', [i.id for i in records])]}
			return res

	#################################################################

	@api.onchange('partner_id','provision_account_id','provision_payment_id')
	def set_domain_for_provision_account_move_line_id(self):
		if (not self.provision_payment_id) and self.partner_id and self.provision_account_id:
			records = []

			records = self.env['account.move.line'].search([
				('move_id.state','in',['posted']),
				('account_id','=',self.provision_account_id.id),
				('partner_id','=',self.partner_id.id),
				'|',
				('amount_residual','>',0.00),
				('amount_residual_currency','>',0.00),
				])

			res = {}
			res['domain'] = {'provision_account_move_line_id': [('id', 'in', [i.id for i in records])]}
			return res

	#################################################################

	@api.onchange('provision_payment_id','partner_id')
	def onchange_provision_account_id(self):
		if self.provision_payment_id and self.partner_id:

			move_line_ids = self.provision_payment_id.mapped('move_id.line_ids').\
				filtered(lambda h : h.account_id.account_type == 'asset_receivable' and \
					h.partner_id == self.partner_id)

			if move_line_ids:
				self.provision_account_id=move_line_ids[0].account_id



	@api.onchange('provision_payment_id','provision_account_id','partner_id')
	def onchange_provision_account_move_line_id(self):
		if self.provision_payment_id and self.provision_account_id and self.partner_id:
			move_line_ids = self.provision_payment_id.mapped('move_id.line_ids').filtered(lambda h : h.account_id ==self.provision_account_id and
				h.partner_id == self.partner_id)
			if move_line_ids:
				self.provision_account_move_line_id=move_line_ids[0]


	############### CALCULANDO POR DEFAULT CUENTA DE DEVOLUCION/REINTEGRO ######
	@api.onchange('provision_payment_id','return_diferencial')
	def onchange_devolucion_reintegro_account_id(self):

		if self.return_diferencial and self.provision_payment_id:
			if self.provision_payment_id.journal_id and self.provision_payment_id.journal_id.suspense_account_id:

				self.devolucion_reintegro_account_id = self.provision_payment_id.journal_id.suspense_account_id

	###################################################################

	@api.depends('provision_payment_id','provision_account_move_line_id')
	def compute_campo_provision_currency_id(self):
		for rec in self:
			if rec.provision_payment_id:
				rec.provision_currency_id = rec.provision_payment_id.currency_id or False

			elif not rec.provision_payment_id and rec.provision_account_move_line_id:
				rec.provision_currency_id = rec.provision_account_move_line_id.currency_id or False



	
	@api.depends('provision_payment_id','provision_payment_id.amount','provision_account_move_line_id')
	def compute_campo_amount_provision_currency(self):
		for rec in self:
			rec.amount_provision_currency = 0.00
			if rec.provision_payment_id:
				rec.amount_provision_currency = rec.provision_payment_id.amount or 0.00

			elif not rec.provision_payment_id and rec.provision_account_move_line_id:
				rec.amount_provision_currency = rec.provision_account_move_line_id.amount_currency or 0.00


	
	@api.depends('provision_account_move_line_id')
	def compute_campo_amount_provision_company_currency(self):
		for rec in self:
			rec.amount_provision_company_currency = 0.00
			if rec.provision_account_move_line_id:
				rec.amount_provision_company_currency = abs(rec.provision_account_move_line_id.balance or 0.00)


	@api.depends('provision_account_move_line_id')
	def compute_campo_amount_residual_provision(self):
		for rec in self:
			rec.amount_residual_provision = 0.00
			if rec.provision_account_move_line_id and rec.provision_account_move_line_id.currency_id != rec.company_id.currency_id:
				rec.amount_residual_provision = abs(rec.provision_account_move_line_id.amount_residual_currency or 0.00)
			else:
				rec.amount_residual_provision = abs(rec.provision_account_move_line_id.amount_residual or 0.00)

	########################################################################################################

	
	@api.depends('rendicion_gastos_line_ids',
		'rendicion_gastos_line_ids.amount_total_rendir_company_currency')
	def compute_campo_amount_rendido_company_currency(self):
		for rec in self:
			rec.amount_rendido_company_currency = 0.00
			if rec.rendicion_gastos_line_ids:
				rec.amount_rendido_company_currency = sum(rec.rendicion_gastos_line_ids.mapped('amount_total_rendir_company_currency'))


	
	@api.depends('rendicion_gastos_sindocumento_line_ids',
		'rendicion_gastos_sindocumento_line_ids.amount_total_company_currency')
	def compute_campo_amount_rendido_sin_documentos_company_currency(self):
		for rec in self:
			rec.amount_rendido_sin_documentos_company_currency = 0.00
			if rec.rendicion_gastos_sindocumento_line_ids:
				rec.amount_rendido_sin_documentos_company_currency = \
					sum(rec.rendicion_gastos_sindocumento_line_ids.mapped('amount_total_company_currency'))

	#########################################################################################################
	
	@api.depends('amount_rendido_company_currency',
		'amount_rendido_sin_documentos_company_currency')
	def compute_campo_amount_rendido_total_company_currency(self):
		for rec in self:
			rec.amount_rendido_total_company_currency = \
				rec.amount_rendido_company_currency + rec.amount_rendido_sin_documentos_company_currency



	@api.depends('amount_rendido_total_company_currency',
		'amount_provision_company_currency')
	def compute_campo_amount_diferencia_total_company_currency(self):
		for rec in self:
			rec.amount_diferencia_total_company_currency = \
				rec.amount_provision_company_currency - rec.amount_rendido_total_company_currency

	#########################################################################################################

	def rendir_gastos(self):

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
				'analytic_distribution':line.analytic_distribution or False,
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

		self.state='send'

	#####################################

	def button_view_move_id(self):
		if self.state == 'send':
			return {
				'name': 'Asiento Contable Rendición de Gastos',
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


	

	def button_view_invoice_ids(self):
		if self.state == 'send':
			invoice_ids = self.rendicion_gastos_line_ids.mapped('invoice_id.id')
			if invoice_ids:
				return {
					'name': 'Facturas de Gastos Rendidas',
					'view_type': 'form',
					'view_mode': 'tree,form',
					'res_model': 'account.move',
					'view_id': False,
					'type': 'ir.actions.act_window',
					'domain': [('id', 'in', list(invoice_ids) or [])],
					'context': {
						'journal_id': self.journal_id.id,
					}
				}