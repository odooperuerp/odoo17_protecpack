import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError

import logging
_logger=logging.getLogger(__name__)

options=[
	('in','esta en'),
	('not in','no esta en')
	]

class PlePurchase(models.Model):
	_name='ple.purchase'
	_inherit='ple.base'
	_description = "Modulo PLE Libros de Compras"
	_rec_name='periodo_ple'

	ple_purchase_line_ids=fields.One2many('ple.purchase.line','ple_purchase_id',string="Registros de compra")
	
	ple_purchase_line_no_domiciliados_ids=fields.One2many('ple.purchase.line','ple_purchase_id_no_domiciliados',
		string="Registros de compra")
	
	ple_purchase_line_recibo_honorarios_ids=fields.One2many('ple.purchase.line','ple_purchase_id_recibo_honorarios',
		string="Registros de compra")
	
	identificador_operaciones = fields.Selection(
		selection=[('0','Cierre de operaciones'),('1','Empresa operativa'),('2','Cierre de libro')],
		string="Identificador de operaciones", required=True, default="1")


	######################### FILTROS DINAMICOS, NUEVOS CAMPOS AGREGADOS !!!
	partner_ids = fields.Many2many('res.partner','ple_purchase_partner_rel','partner_id','ple_purchase_id_1',string="Socio")
	journal_ids = fields.Many2many('account.journal','ple_purchase_journal_rel','journal_id','ple_purchase_id_3',string="Diario")
	move_ids = fields.Many2many('account.move','ple_purchase_move_rel','move_id','ple_purchase_id_4',string='Asiento Contable')
	currency_ids = fields.Many2many('res.currency','ple_purchase_currency_rel','currency_id','ple_purchase_id_6',string="Moneda")
	##################################################################################
	partner_option=fields.Selection(selection=options , string="")
	journal_option=fields.Selection(selection=options , string="")
	move_option=fields.Selection(selection=options , string="")
	currency_option=fields.Selection(selection=options , string="")

	########################################################
	## CAMPO PARA IMPRIMIR RECIBO POR HONORARIOS EN LOS REPORTES DE DOMICILIADOS

	fecha=fields.Boolean(string="Fecha")
	periodo=fields.Boolean(string="Periodo")

	date_from=fields.Date(string="Desde:")
	date_to=fields.Date(string="Hasta:")

	fecha_inicio = fields.Date(string="Fecha Inicio")
	fecha_fin = fields.Date(string="Fecha Fin")

	periodo_ple=fields.Char(string="Periodo",compute="compute_campo_periodo",store=True)
	############## CHECK para indicar si se incluye o no registros anteriores no declarados
	
	incluir_anteriores_no_declarados = fields.Boolean(string="Incluir registros anteriores no declarados",
		default=False)


	@api.depends('fiscal_year','fiscal_month')
	def compute_campo_periodo(self):
		for ple in self:
			if ple.fiscal_year and ple.fiscal_month:
				ple.periodo_ple = "%s-%s-00" % (ple.fiscal_year or 'YYYY', ple.fiscal_month or 'MM') 
			else:
				ple.periodo_ple = 'Nuevo Registro'


	def open_wizard_print_form(self):
		res = super(PlePurchase,self).open_wizard_print_form()

		view = self.env.ref('ple_purchase.view_wizard_printer_ple_purchase_form')
		if view:

			return {
				'name': _('FORMULARIO DE IMPRESIÓN DEL LIBRO PLE'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'wizard.printer.ple.purchase',
				'views': [(view.id,'form')],
				'view_id': view.id,
				'target': 'new',
				'context': {
					'default_ple_purchase_id': self.id,
					'default_company_id' : self.company_id.id,}}
	######################################

	def button_view_tree_domiciliados(self):
		self.ensure_one()
		view = self.env.ref('ple_purchase.view_ple_purchase_domiciliados_line_tree')
		if self.ple_purchase_line_ids:
			diccionario = {
				'name': 'Libro PLE Compras Domiciliadas',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'ple.purchase.line',
				'view_id': view.id,
				'views': [(view.id,'tree')],
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', [i.id for i in self.ple_purchase_line_ids] or [])],
				'context':{
					'search_default_filter_proveedor':1,
					'search_default_filter_tipo_comprobante':1,
					}
			}
			return diccionario

	#############################################
	def button_view_tree_recibo_honorarios(self):
		self.ensure_one()
		view = self.env.ref('ple_purchase.view_ple_purchase_domiciliados_line_tree')
		if self.ple_purchase_line_ids:
			diccionario = {
				'name': 'Libro PLE Compras Recibo Honorarios',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'ple.purchase.line',
				'view_id': view.id,
				'views': [(view.id,'tree')],
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', [i.id for i in self.ple_purchase_line_recibo_honorarios_ids] or [])],
				'context':{
					'search_default_filter_proveedor':1,
					'search_default_filter_tipo_comprobante':1,
					}
			}
			return diccionario

	###########################################
	def button_view_tree_no_domiciliados(self):
		self.ensure_one()
		view = self.env.ref('ple_purchase.view_ple_purchase_no_domiciliados_line_tree')
		if self.ple_purchase_line_ids:
			diccionario = {
				'name': 'Libro PLE Compras No Domiciliadas',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'ple.purchase.line',
				'view_id': view.id,
				'views': [(view.id,'tree')],
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', [i.id for i in self.ple_purchase_line_no_domiciliados_ids] or [])],
				'context':{
					'search_default_filter_proveedor':1,
					'search_default_filter_tipo_comprobante':1,
					}
			}
			return diccionario
	#############################################

			
	@api.onchange('fecha')
	def onchange_fecha(self):
		for rec in self:
			if rec.fecha:
				rec.periodo=False

	@api.onchange('periodo')
	def onchange_periodo(self):
		for rec in self:
			if rec.periodo:
				rec.fecha=False

	#######################################
	def unlink (self):
		for line in self:
			for line2 in line.ple_purchase_line_ids + self.ple_purchase_line_no_domiciliados_ids + line.ple_purchase_line_recibo_honorarios_ids:
				line2.move_id.write({'declared_ple_8_1_8_2':False})
			return super(PlePurchase,line).unlink()



	def _action_confirm_ple(self):
		array_id=[]
		for line in self.ple_purchase_line_ids + self.ple_purchase_line_no_domiciliados_ids + self.ple_purchase_line_recibo_honorarios_ids:
			array_id.append(line.move_id.id)
		# self.env['account.move'].browse(array_id).write({'declared_ple':True})
		super(PlePurchase , self)._action_confirm_ple('account.move' , array_id ,{'declared_ple_8_1_8_2':True})

	
	def _get_datas(self, domain):
		orden =''
		if self.print_order == 'date':
			orden = "invoice_date asc"		
		elif self.print_order == 'invoice_number':
			orden = "name asc"
		return self._get_query_datas('account.move', domain, orden)


	def _get_order_print(self , object):
		total =''
		if self.print_order == 'date':
			total=sorted(object, key=lambda PlePurchaseLine: PlePurchaseLine.fecha_emision_comprobante)
		elif self.print_order == 'invoice_number':
			total=sorted(object , key=lambda PlePurchaseLine: PlePurchaseLine.numero_comprobante)
		return total


	##########################################################################

	def _get_domain(self):

		filter_clause = ""

		if self.fecha:
			self.fecha_inicio=self.date_from
			self.fecha_fin=self.date_to
			
		elif self.periodo:
			if self.incluir_anteriores_no_declarados:
				self.fecha_inicio= "%s-01-01" %(self.fiscal_year)
				self.fecha_fin= self._get_end_date()
			else:
				self.fecha_inicio= self._get_star_date()
				self.fecha_fin= self._get_end_date()
		#####################

		filter_clause += """ and am.date >= '%s' and am.date <= '%s' and 
			am.declared_ple_8_1_8_2 is not True """%(
			self.fecha_inicio.strftime("%Y-%m-%d"),
			self.fecha_fin.strftime("%Y-%m-%d"))


		partners=tuple(self.partner_ids.mapped('id'))
		len_partners = len(partners or '')
		if len_partners:
			filter_clause += " and am.partner_id %s %s" % (self.partner_option or 'in', str(partners) if len_partners!=1 else str(partners)[0:len(str(partners))-2] + ')')


		journals = tuple(self.journal_ids.mapped('id'))
		len_journals = len(journals or '')
		if len(self.journal_ids):
			filter_clause += " and am.journal_id %s %s " % (self.journal_option or 'in', str(journals) if len_journals!=1 else str(journals)[0:len(str(journals))-2] + ')')


		moves = tuple(self.move_ids.mapped('id'))
		len_moves = len(moves or '')
		if len(moves):
			filter_clause += " and am.id %s %s " % (self.move_option or 'in', str(moves) if len_moves!=1 else str(moves)[0:len(str(moves))-2] + ')')

		
		currencys = tuple(self.currency_ids.mapped('id'))
		len_currencys = len(currencys or '')
		if len(self.currency_ids):
			filter_clause += " and am.currency_id %s %s " % (self.currency_option or 'in', str(currencys) if len_currencys!=1 else str(currencys)[0:len(str(currencys))-2] + ')')
		

		return filter_clause

	########################################################################


	def _periodo_fiscal(self):
		periodo = "%s%s00" % (self.fiscal_year or 'YYYY', self.fiscal_month or 'MM')
		return periodo


	###############################################
	def type_document_parent(self,invoice):
		parent_type=''
		if invoice.reversed_entry_id:
			parent_type= invoice.reversed_entry_id.l10n_latam_document_type_id and \
				invoice.reversed_entry_id.l10n_latam_document_type_id.code or ''
		
		return parent_type


	def alarm_fecha_periodo(self):
		for rec in self:
			if rec.fecha:
				if not rec.date_from or not rec.date_to:
					raise UserError(_('NO SE PUEDE GENERAR EL LIBRO!!\nLos campos: Fecha Desde y Fecha Hasta son obligatorios.'))
			elif rec.periodo:
				if not rec.fiscal_year or not rec.fiscal_month:
					raise UserError(_('NO SE PUEDE GENERAR EL LIBRO!!\nLos campos: Año y mes Fiscal son obligatorios.'))
			else:
				raise UserError(_('NO SE PUEDE GENERAR EL LIBRO!!\nElija la opción Fecha o Periodo para generar el Libro.'))


	#################################################
	def get_query_ple_purchase(self):

		query = """
			select 
			%s as ple_purchase_id,
			%s as ple_purchase_id_no_domiciliados,
			%s as ple_purchase_id_recibo_honorarios,
			am.id as move_id,
			am.journal_id as journal_id,
			am.partner_id as partner_id,
			rp.country_id as partner_country_id,
			rp.street as no_domiciliado_domicilio,
			rco.code_sunat as no_domiciliado_pais_residencia,
			rp.vat as no_domiciliado_numero_identificacion,
			am.currency_id as currency_id,
			am2.id as move_id_2,
			am.name as asiento_contable,
			'M1' as m_correlativo_asiento_contable,
			'M1' as no_domiciliado_m_correlativo_asiento_contable,
			am.invoice_date as fecha_emision_comprobante,
			am.invoice_date_due as fecha_vencimiento,
			case
				when am.l10n_latam_document_type_id is not null then coalesce(lldt.code,'')
				else '' 
			end tipo_comprobante,
			am.l10n_pe_prefix_code as serie_comprobante,
			am.l10n_pe_invoice_number as numero_comprobante,
			
			case
				when am.partner_id is not null and rp.l10n_latam_identification_type_id is not null 
					then coalesce(llit.l10n_pe_vat_code,'')
				else ''
			end tipo_documento_proveedor,

			case 
				when am.partner_id is not null then coalesce(rp.vat,'')
				else ''
			end ruc_dni,

			case 
				when am.partner_id is not null then coalesce(rp.name,'')
				else ''
			end razon_social,

			case
				when am.l10n_latam_document_type_id is not null then 
					case 
						when coalesce(lldt.code,'') = '50' then EXTRACT(YEAR FROM am.invoice_date)
						else '0'
					end
				else '0' 
			end anio_emision_dua,

			case 
				when am.move_type = 'in_refund' then 
					case 
						when am.reversed_entry_id is not null then round(coalesce(am2.currency_tc,1.00),3)
						else round(coalesce(am.currency_tc,1.00),3)
					end
				
				else round(coalesce(am.currency_tc,1.00),3)
			end tipo_cambio,

			case 
				when am.move_type = 'in_refund' then 
					case
						when am.reversed_entry_id is not null then 
							(-1.00)*coalesce(am.total_sale_taxed,0.00)*round(coalesce(am2.currency_tc,1.00),3)

						else
							(-1.00)*coalesce(am.total_sale_taxed,0.00)*round(coalesce(am.currency_tc,1.00),3)
							
					end
					
				else 
					coalesce(am.total_sale_taxed,0.00)*round(coalesce(am.currency_tc,1.00),3)
			end base_imponible_igv_gravadas,

			case 
				when am.move_type = 'in_refund' then 
					case
						when am.reversed_entry_id is not null then 
							(-1.00)*coalesce(am.total_sale_igv,0.00)*round(coalesce(am2.currency_tc,1.00),3)

						else
							(-1.00)*coalesce(am.total_sale_igv,0.00)*round(coalesce(am.currency_tc,1.00),3)
									
					end
							
				else 
					coalesce(am.total_sale_igv,0.00)*round(coalesce(am.currency_tc,1.00),3)
			end monto_igv_1,

			case 
				when am.move_type = 'in_refund' then 
					case
						when am.reversed_entry_id is not null then 
							(-1.00)*(coalesce(am.total_sale_free,0.00) + coalesce(am.total_sale_unaffected,0.00) + coalesce(am.total_sale_exonerated,0.00))*round(coalesce(am2.currency_tc,1.00),3)

						else
							(-1.00)*(coalesce(am.total_sale_free,0.00) + coalesce(am.total_sale_unaffected,0.00) + coalesce(am.total_sale_exonerated,0.00))*round(coalesce(am.currency_tc,1.00),3)
									
					end
							
				else 
					(coalesce(am.total_sale_free,0.00) + coalesce(am.total_sale_unaffected,0.00) + coalesce(am.total_sale_exonerated,0.00))*round(coalesce(am.currency_tc,1.00),3)
			end valor_no_gravadas,

			case 
				when am.move_type = 'in_refund' then 
					case
						when am.reversed_entry_id is not null then 
							(-1.00)*coalesce(am.total_venta,0.00)*round(coalesce(am2.currency_tc,1.00),3)

						else
							(-1.00)*coalesce(am.total_venta,0.00)*round(coalesce(am.currency_tc,1.00),3)
											
					end
									
				else 
					coalesce(am.total_venta,0.00)*round(coalesce(am.currency_tc,1.00),3)
			end importe_adquisiciones_registradas,

			0.00 as otros_impuestos,
			0.00 as impuesto_consumo_bolsas_plastico,

			case 
				when am.currency_id is not null then coalesce(rc.name,'')
				else ''
			end codigo_moneda,

			case 
				when ad.id is not null then ad.fecha_pago
				else null
			end fecha_detraccion, 

			case 
				when ad.id is not null then coalesce(ad.nro_constancia,'')
				else null
			end numero_detraccion, 

			case 
				when am2.id is not null then am2.invoice_date
				else null
			end fecha_emision_original,

			case 
				when am2.id is not null then
					case
						when am2.l10n_latam_document_type_id is not null then coalesce(lldt2.code,'')
						else ''
					end	
				else null
			end tipo_comprobante_original,

			case 
				when am2.id is not null then coalesce(am2.l10n_pe_prefix_code,'')
				else ''
			end serie_comprobante_original,			

			case 
				when am2.id is not null then coalesce(am2.l10n_pe_invoice_number,'')
				else ''
			end numero_comprobante_original

			from account_move as am 
			left join account_move am2 on am2.id = am.reversed_entry_id 
			left join res_partner rp on rp.id = am.partner_id 
			left join res_currency rc on rc.id = am.currency_id 
			left join res_country rco on rco.id = rp.country_id
			left join l10n_latam_document_type lldt on lldt.id = am.l10n_latam_document_type_id 
			left join l10n_latam_document_type lldt2 on lldt2.id = am2.l10n_latam_document_type_id 
			left join l10n_latam_identification_type llit on llit.id = rp.l10n_latam_identification_type_id 
			left join account_detraction ad on ad.id = am.register_detraction_id 
			where am.move_type in ('in_invoice','in_refund') and am.state in ('posted') and am.company_id = %s """%(
				self.id,
				self.id,
				self.id,
				self.company_id.id,
				)

		return query


	############################################################################

	def get_fields_insert_into(self):
		query = """ 
			insert into ple_purchase_line (
			ple_purchase_id,
			ple_purchase_id_no_domiciliados,
			ple_purchase_id_recibo_honorarios,
			move_id,
			journal_id,
			partner_id,
			partner_country_id,
			no_domiciliado_domicilio,
			no_domiciliado_pais_residencia,
			no_domiciliado_numero_identificacion,
			currency_id,
			move_id_2,
			asiento_contable,
			m_correlativo_asiento_contable,
			no_domiciliado_m_correlativo_asiento_contable,
			fecha_emision_comprobante,
			fecha_vencimiento,
			tipo_comprobante,
			serie_comprobante,
			numero_comprobante,
			tipo_documento_proveedor,
			ruc_dni,
			razon_social,
			anio_emision_dua,
			tipo_cambio,
			base_imponible_igv_gravadas,
			monto_igv_1,
			valor_no_gravadas,
			importe_adquisiciones_registradas,
			otros_impuestos,
			impuesto_consumo_bolsas_plastico,
			codigo_moneda,
			fecha_detraccion,
			numero_detraccion,
			fecha_emision_original,
			tipo_comprobante_original,
			serie_comprobante_original,
			numero_comprobante_original
			)  """
		return query


	#################################################################

	def generar_libro(self):

		self.alarm_fecha_periodo()

		registro=[]
		
		self.state='open'
		self.ple_purchase_line_ids.unlink()
		self.ple_purchase_line_recibo_honorarios_ids.unlink()
		self.ple_purchase_line_no_domiciliados_ids.unlink()

		filter_clause = self._get_domain()

		query_general = self.get_query_ple_purchase()

		if filter_clause:
			query_general += filter_clause


		query_insert_into_general = self.get_fields_insert_into()

		query_total_general = "%s %s"%(query_insert_into_general or '',query_general or '')

		self.env.cr.execute(query_total_general)

		self.update_ple_purchase_line_type()
	

	####################################################################

	def update_ple_purchase_line_type(self):

		query = """
			update ple_purchase_line set 

			ple_purchase_id_recibo_honorarios = 
			(case
			when tipo_documento_proveedor is not Null and tipo_documento_proveedor <> '0' and 
			tipo_comprobante is not Null and tipo_comprobante = '02' then %s 
			else Null end),
			ple_purchase_id = 
			(case
			when tipo_documento_proveedor is not Null and tipo_documento_proveedor <> '0' and 
			tipo_comprobante is not Null and tipo_comprobante not in ('02','91','97','98') then %s 
			else Null end),
			ple_purchase_id_no_domiciliados = 
			(case
			when tipo_documento_proveedor is not Null and tipo_documento_proveedor = '0' and 
			tipo_comprobante is not Null and tipo_comprobante in ('91','97','98') then %s 
			else Null end)

			where ple_purchase_id = %s or ple_purchase_id_no_domiciliados = %s or 
			ple_purchase_id_recibo_honorarios = %s
			""" % (self.id,self.id,self.id,self.id,self.id,self.id)

		self.env.cr.execute(query)

	#####################################################################


	"""def generar_libro(self):

		self.alarm_fecha_periodo()
		
		registro=[]
		registro_no_domiciliados=[]
		registro_recibo_honorarios=[]

		self.state='open'
		self.ple_purchase_line_ids.unlink()
		self.ple_purchase_line_recibo_honorarios_ids.unlink()
		self.ple_purchase_line_no_domiciliados_ids.unlink()


		query = self.get_query_ple_purchase()

		filter_clause = self._get_domain()

		if filter_clause:
			query += filter_clause

		self.env.cr.execute(query)
		records = self.env.cr.dictfetchall()
		
		####################################################
		for line in records:

			move_id = self.env['account.move'].browse(line['move_id'])

			if line['tipo_comprobante'] and (line['tipo_comprobante'] in ['02']) or (self.type_document_parent(move_id) in ['02']):
				
				registro_recibo_honorarios.append((0,0,{
					'fiscal_year':str(self.fiscal_year or ''),
					'fiscal_month':str(self.fiscal_month or ''),
					'move_id':line['move_id'] or False,
					'journal_id':line['journal_id'] or False,
					'partner_id':line['partner_id'] or False,
					'partner_country_id':line['partner_country_id'] or False,
					'currency_id':line['currency_id'] or False,
					'move_id_2':line['move_id_2'] or False,
					'asiento_contable':line['asiento_contable'] or '',
					'm_correlativo_asiento_contable':line['m_correlativo_asiento_contable'] or '',
					'fecha_emision_comprobante':line['fecha_emision_comprobante'] or False,
					'fecha_vencimiento':line['fecha_vencimiento'] or False,
					'tipo_comprobante':line['tipo_comprobante'] or '',
					'serie_comprobante':line['serie_comprobante'] or '',
					'numero_comprobante':line['numero_comprobante'] or '',
					'tipo_documento_proveedor':line['tipo_documento_proveedor'] or '',
					'ruc_dni':line['ruc_dni'] or '',
					'razon_social':line['razon_social'] or '',
					'tipo_cambio':line['tipo_cambio'] or 1.00,
					'codigo_moneda':line['codigo_moneda'] or '',
					'fecha_emision_original':line['fecha_emision_original'] or False,
					'tipo_comprobante_original':line['tipo_comprobante_original'] or '',
					'serie_comprobante_original':line['serie_comprobante_original'] or '',
					'numero_comprobante_original':line['numero_comprobante_original'] or '',
				}))

			else:

				if str(move_id.partner_id and move_id.partner_id.l10n_latam_identification_type_id and move_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '').strip() not in  ['0'] and\
					(line['tipo_comprobante'] and line['tipo_comprobante'] not in ['91','97','98']):
					
					registro.append((0,0,{
						'fiscal_year':str(self.fiscal_year or ''),
						'fiscal_month':str(self.fiscal_month or ''),
						'move_id':line['move_id'] or False,
						'journal_id':line['journal_id'] or False,
						'partner_id':line['partner_id'] or False,
						'partner_country_id':line['partner_country_id'] or False,
						'currency_id':line['currency_id'] or False,
						'move_id_2':line['move_id_2'] or False,
						'asiento_contable':line['asiento_contable'] or '',
						'm_correlativo_asiento_contable':line['m_correlativo_asiento_contable'] or '',
						'fecha_emision_comprobante':line['fecha_emision_comprobante'] or False,
						'fecha_vencimiento':line['fecha_vencimiento'] or False,
						'tipo_comprobante':line['tipo_comprobante'] or '',
						'serie_comprobante':line['serie_comprobante'] or '',
						'numero_comprobante':line['numero_comprobante'] or '',
						'tipo_documento_proveedor':line['tipo_documento_proveedor'] or '',
						'ruc_dni':line['ruc_dni'] or '',
						'razon_social':line['razon_social'] or '',
						'tipo_cambio':line['tipo_cambio'] or '',
						'codigo_moneda':line['codigo_moneda'] or '',
						'fecha_emision_original':line['fecha_emision_original'] or False,
						'tipo_comprobante_original':line['tipo_comprobante_original'] or '',
						'serie_comprobante_original':line['serie_comprobante_original'] or '',
						'numero_comprobante_original':line['numero_comprobante_original'] or '',
					}))

				elif str(move_id.partner_id and move_id.partner_id.l10n_latam_identification_type_id and move_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '').strip() in ['0'] and\
					(line['tipo_comprobante'] and line['tipo_comprobante'] in ['91','97','98']):

					registro_no_domiciliados.append((0,0,{
						'fiscal_year':str(self.fiscal_year or ''),
						'fiscal_month':str(self.fiscal_month or ''),
						'move_id':line['move_id'] or False,
						'journal_id':line['journal_id'] or False,
						'partner_id':line['partner_id'] or False,
						'partner_country_id':line['partner_country_id'] or False,
						'currency_id':line['currency_id'] or False,
						'move_id_2':line['move_id_2'] or False,
						'asiento_contable':line['asiento_contable'] or '',
						'm_correlativo_asiento_contable':line['m_correlativo_asiento_contable'] or '',
						'fecha_emision_comprobante':line['fecha_emision_comprobante'] or False,
						'fecha_vencimiento':line['fecha_vencimiento'] or False,
						'tipo_comprobante':line['tipo_comprobante'] or '',
						'serie_comprobante':line['serie_comprobante'] or '',
						'numero_comprobante':line['numero_comprobante'] or '',
						'tipo_documento_proveedor':line['tipo_documento_proveedor'] or '',
						'ruc_dni':line['ruc_dni'] or '',
						'razon_social':line['razon_social'] or '',
						'tipo_cambio':line['tipo_cambio'] or '',
						'codigo_moneda':line['codigo_moneda'] or '',
						'fecha_emision_original':line['fecha_emision_original'] or False,
						'tipo_comprobante_original':line['tipo_comprobante_original'] or '',
						'serie_comprobante_original':line['serie_comprobante_original'] or '',
						'numero_comprobante_original':line['numero_comprobante_original'] or '',
						'no_domiciliado_domicilio':line['no_domiciliado_domicilio'] or '',
						'no_domiciliado_pais_residencia':line['no_domiciliado_pais_residencia'] or '',
						'no_domiciliado_numero_identificacion':line['no_domiciliado_numero_identificacion'] or '',
						'no_domiciliado_m_correlativo_asiento_contable':line['no_domiciliado_m_correlativo_asiento_contable'] or '',

					}))

		self.ple_purchase_line_ids = registro
		self.ple_purchase_line_recibo_honorarios_ids=registro_recibo_honorarios
		self.ple_purchase_line_no_domiciliados_ids=registro_no_domiciliados
	"""

	####################################################################

	def _convert_object_date(self, date):
		# parametro date que retorna un valor vacio o el formato 01/01/2100 dia/mes/año
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''