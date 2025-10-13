import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError

import logging
_logger=logging.getLogger(__name__)

options = [('in','Esta en'),('not in','No esta en')]

class PleSale(models.Model):
	_name='ple.sale'
	_inherit='ple.base'
	_description = "Modulo PLE Libros de Ventas"
	_rec_name='periodo_ple'

	ple_sale_line_ids=fields.One2many('ple.sale.line','ple_sale_id',string="Registros de venta")

	ple_sale_subtotales_line_ids=fields.One2many('ple.sale.subtotales.line','ple_sale_id',
		string="Subtotales en Registros Ventas")


	partner_ids = fields.Many2many('res.partner','ple_sale_partner_rel','partner_id','ple_sale_id_1',string="Socio")
	journal_ids = fields.Many2many('account.journal','ple_sale_journal_rel','journal_id','ple_sale_id_3',string="Diario")
	move_ids = fields.Many2many('account.move','ple_sale_move_rel','move_id','ple_sale_id_4',string='Factura')
	currency_ids = fields.Many2many('res.currency','ple_sale_currency_rel','currency_id','ple_sale_id_6',string="Moneda")

	####### Select Option Filter
	partner_option=fields.Selection(selection=options,string="")
	journal_option=fields.Selection(selection=options,string="")
	move_option=fields.Selection(selection=options,string="")
	currency_option=fields.Selection(selection=options,string="")
	#######################

	fecha=fields.Boolean(string="Fecha")
	periodo=fields.Boolean(string="Periodo")

	date_from=fields.Date(string="Desde:")
	date_to=fields.Date(string="Hasta:")

	fecha_inicio = fields.Date(string="Fecha Inicio")
	fecha_fin = fields.Date(string="Fecha Fin")

	periodo_ple=fields.Char(string="Periodo PLE Ventas",compute="compute_campo_periodo",store=True)

	############## CHECK para indicar si se incluye o no registros anteriores no declarados
	
	incluir_anteriores_no_declarados = fields.Boolean(string="Incluir registros anteriores no declarados", default=False)

	###############################
	_sql_constraints = [
		('fiscal_month', 'unique(fiscal_month,fiscal_year,company_id)',  'Este periodo para el PLE ya existe , revise sus registros de PLE creados!!!'),
	]


	########################################################################
	

	def compute_campo_sub_totales(self):

		query = """
			select 
				tipo_comprobante_id, 
				sum(coalesce(ventas_valor_facturado_exportacion,0.00)) as ventas_valor_facturado_exportacion,
				sum(coalesce(ventas_base_imponible_operacion_gravada,0.00)) as ventas_base_imponible_operacion_gravada,
				sum(coalesce(ventas_descuento_base_imponible,0.00)) as ventas_descuento_base_imponible,
				sum(coalesce(ventas_igv,0.00)) as ventas_igv,
				sum(coalesce(ventas_descuento_igv,0.00)) as ventas_descuento_igv,
				sum(coalesce(isc,0.00)) as isc,
				sum(coalesce(ventas_importe_operacion_exonerada,0.00)) as ventas_importe_operacion_exonerada,
				sum(coalesce(ventas_importe_operacion_inafecta,0.00)) as ventas_importe_operacion_inafecta,
				sum(coalesce(ventas_base_imponible_arroz_pilado,0.00)) as ventas_base_imponible_arroz_pilado,
				sum(coalesce(ventas_impuesto_arroz_pilado,0.00)) as ventas_impuesto_arroz_pilado,
				sum(coalesce(impuesto_consumo_bolsas_plastico,0.00)) as impuesto_consumo_bolsas_plastico,
				sum(coalesce(otros_impuestos,0.00)) as otros_impuestos,
				sum(coalesce(importe_total_comprobante,0.00)) as importe_total_comprobante
			from ple_sale_line
			where ple_sale_id = %s group by tipo_comprobante_id""" %(self.id)

		self.env.cr.execute(query)

		records = self.env.cr.dictfetchall()

		self.ple_sale_subtotales_line_ids.unlink()

		registro=[]

		if records:
			for line in records:

				registro.append((0,0,{
					'tipo_comprobante_id': line['tipo_comprobante_id'] or False,
					'ventas_valor_facturado_exportacion': line['ventas_valor_facturado_exportacion'] or 0.00,
					'ventas_base_imponible_operacion_gravada': line['ventas_base_imponible_operacion_gravada'] or 0.00,
					'ventas_descuento_base_imponible': line['ventas_descuento_base_imponible'] or 0.00,
					'ventas_igv': line['ventas_igv'] or 0.00,
					'ventas_descuento_igv': line['ventas_descuento_igv'] or 0.00,
					'isc': line['isc'] or 0.00,
					'ventas_importe_operacion_exonerada': line['ventas_importe_operacion_exonerada'] or 0.00,
					'ventas_importe_operacion_inafecta': line['ventas_importe_operacion_inafecta'] or 0.00,
					'ventas_base_imponible_arroz_pilado': line['ventas_base_imponible_arroz_pilado'] or 0.00,
					'ventas_impuesto_arroz_pilado': line['ventas_impuesto_arroz_pilado'] or 0.00,
					'impuesto_consumo_bolsas_plastico': line['impuesto_consumo_bolsas_plastico'] or 0.00,
					'otros_impuestos': line['otros_impuestos'] or 0.00,
					'importe_total_comprobante': line['importe_total_comprobante'] or 0.00,
					}))

			self.ple_sale_subtotales_line_ids = registro


	############################################################################

	@api.depends(
		'fiscal_year',
		'fiscal_month',
		'periodo',
		'fecha',
		'date_from',
		'date_to',
		'incluir_anteriores_no_declarados',
		'partner_ids',
		'journal_ids',
		'move_ids',
		'currency_ids')
	def compute_campo_periodo(self):
		for ple in self:

			ple.periodo_ple = ''

			cad = ""
			if ple.periodo:
				cad = "PERIODO: %s-%s-00" % (
					ple.fiscal_year or 'YYYY', 
					ple.fiscal_month or 'MM')

			elif ple.fecha:
				cad = "FECHA: DEL %s AL %s" % (
					ple.date_from and ple.date_from.strftime("%Y-%m-%d") or '',
					ple.date_to and ple.date_to.strftime("%Y-%m-%d") or '')
			else:
				cad = 'NUEVO REGISTRO'


			if ple.incluir_anteriores_no_declarados:
				cad += " ANTERIORES INCLUIDOS"

			if ple.partner_ids or ple.journal_ids or ple.move_ids or ple.currency_ids:
				cad += " CON FILTROS"

			ple.periodo_ple = cad or ''



	def open_wizard_print_form(self):
		res = super(PleSale,self).open_wizard_print_form()

		view = self.env.ref('ple_sale.view_wizard_printer_ple_sale_form')
		if view:

			return {
				'name': _('FORMULARIO DE IMPRESIÓN DEL LIBRO PLE'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'wizard.printer.ple.sale',
				'views': [(view.id,'form')],
				'view_id': view.id,
				'target': 'new',
				'context': {
					'default_ple_sale_id': self.id,
					'default_company_id' : self.company_id.id,}}

	######################################
	def button_view_tree_ple_sale_lines(self):
		self.ensure_one()
		view = self.env.ref('ple_sale.view_ple_sale_line_tree')
		if self.ple_sale_line_ids:
			diccionario = {
				'name': 'Libro PLE Ventas',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'ple.sale.line',
				'view_id': view.id,
				'views': [(view.id,'tree')],
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', [i.id for i in self.ple_sale_line_ids] or [])],
				'context':{
					'search_default_filter_cliente':1,
					'search_default_filter_tipo_comprobante':1,
					}
			}
			return diccionario

	###########################################

	def name_get(self):
		result = []
		for ple in self:
			if ple.periodo:
				result.append((ple.id, ple._periodo_fiscal() or 'New'))
			elif ple.fecha:
				result.append((ple.id,"%s-%s"%(self._convert_object_date(ple.date_from),self._convert_object_date(ple.date_to)) or 'New'))
			else:
				result.append((ple.id,'New'))
		return result


	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		if self.periodo:
			recs = self.search([('fiscal_month', operator, name),('fiscal_year', operator, name)] + args, limit=limit)
		elif self.fecha:
			recs = self.search([('date_from', operator, name),('date_to', operator, name)] + args, limit=limit)
		return recs.name_get()
	###############################################

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


	def unlink (self):
		for line in self:
			for line2 in line.ple_sale_line_ids:
				line2.invoice_id.write({'declared_ple':False})
			return super(PleSale, line).unlink()


	def criterios_impresion(self):
		res = super(PleSale, self).criterios_impresion() or []
		res += [('invoice_number',u'N° de documento'),('num_serie',u'N° de serie'),('table10_id','Tipo de documento')]
		return res


	def _action_confirm_ple(self):
		array_id=[]
		for line in self.ple_sale_line_ids :
			array_id.append(line.invoice_id.id)
		super(PleSale ,self)._action_confirm_ple('account.move' ,array_id,{'declared_ple':True})

	def _get_datas(self, domain):
		return self._get_query_datas('account.move', domain, "invoice_date asc , name asc")


	##############################################
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

		filter_clause += " and am.date >= '%s' and am.date <= '%s' "%(
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


	#########################################################################################
	def get_query_ple_sale(self):

		query = """
			select 
			%s as ple_sale_id,
			am.id as move_id,
			am2.id as invoice_id_2,
			am.name as asiento_contable,
			'M1' as m_correlativo_asiento_contable,
			am.invoice_date as fecha_emision_comprobante,
			am.invoice_date_due as fecha_vencimiento,
			case
				when am.l10n_latam_document_type_id is not null then coalesce(lldt.code,'')
				else '' 
			end tipo_comprobante,
			am.l10n_latam_document_type_id as tipo_comprobante_id, 
			am.l10n_pe_prefix_code as serie_comprobante,
			am.l10n_pe_invoice_number as numero_comprobante,
			am.partner_id as partner_id,
			case 
				when am.state = 'posted' then
					case 
						when am.partner_id is not null and rp.l10n_latam_identification_type_id is not null 
							then coalesce(llit.l10n_pe_vat_code,'')
						else ''
					end
				when am.state = 'cancel' then ''
			end tipo_documento_cliente,
			case 
				when am.state = 'posted' then 
					case 
						when am.partner_id is not null then coalesce(rp.vat,'')
						else ''
					end	
				when am.state = 'cancel' then 
					case 
						when am.partner_id is not null then '00000000'
						else ''
					end
			end numero_documento_cliente,

			case 
				when am.state = 'posted' then 
					case 
						when am.partner_id is not null then coalesce(rp.name,'')
						else ''
					end	
				when am.state = 'cancel' then 
					case 
						when am.partner_id is not null then 'ANULADO'
						else ''
					end
			end razon_social,

			case 
				when am.move_type = 'out_refund' then 
					case 
						when am.reversed_entry_id is not null then round(coalesce(am2.currency_tc,1.00),3)
						else round(coalesce(am.currency_tc,1.00),3)
					end
				
				else round(coalesce(am.currency_tc,1.00),3)
			end tipo_cambio,

			case 
				when am.move_type = 'out_refund' then 
					case
						when am.reversed_entry_id is not null then 
							case 
								when am.state != 'cancel' then 
									(-1.00)*coalesce(am.total_sale_export,0.00)*round(coalesce(am2.currency_tc,1.00),3)
						
								else 0.00
							end

						else
							case 
								when am.state != 'cancel' then 
									(-1.00)*coalesce(am.total_sale_export,0.00)*round(coalesce(am.currency_tc,1.00),3)
						
								else 0.00
							end
					end
				
				else 
					case
						when am.state != 'cancel' then 
							coalesce(am.total_sale_export,0.00)*round(coalesce(am.currency_tc,1.00),3)
						else 0.00
					end
			end ventas_valor_facturado_exportacion,

			case 
				when am.move_type = 'out_refund' then 
					case
						when am.reversed_entry_id is not null then 
							case 
								when am.state != 'cancel' then 
									(-1.00)*coalesce(am.total_sale_taxed,0.00)*round(coalesce(am2.currency_tc,1.00),3)
						
								else 0.00
							end

						else
							case 
								when am.state != 'cancel' then 
									(-1.00)*coalesce(am.total_sale_taxed,0.00)*round(coalesce(am.currency_tc,1.00),3)
						
								else 0.00
							end
					end
				
				else 
					case
						when am.state != 'cancel' then 
							coalesce(am.total_sale_taxed,0.00)*round(coalesce(am.currency_tc,1.00),3)
						else 0.00
					end
			end ventas_base_imponible_operacion_gravada,

			case 
				when am.move_type = 'out_refund' then 
					case
						when am.reversed_entry_id is not null then 
							case 
								when am.state != 'cancel' then 
									(-1.00)*coalesce(am.total_sale_exonerated,0.00)*round(coalesce(am2.currency_tc,1.00),3)
						
								else 0.00
							end

						else
							case 
								when am.state != 'cancel' then 
									(-1.00)*coalesce(am.total_sale_exonerated,0.00)*round(coalesce(am.currency_tc,1.00),3)
						
								else 0.00
							end
					end
				
				else 
					case
						when am.state != 'cancel' then 
							coalesce(am.total_sale_exonerated,0.00)*round(coalesce(am.currency_tc,1.00),3)
						else 0.00
					end
			end ventas_importe_operacion_exonerada,

			case 
				when am.move_type = 'out_refund' then 
					case
						when am.reversed_entry_id is not null then 
							case 
								when am.state != 'cancel' then 
									(-1.00)*coalesce(am.total_sale_unaffected,0.00)*round(coalesce(am2.currency_tc,1.00),3)
						
								else 0.00
							end

						else
							case 
								when am.state != 'cancel' then 
									(-1.00)*coalesce(am.total_sale_unaffected,0.00)*round(coalesce(am.currency_tc,1.00),3)
						
								else 0.00
							end
					end
				
				else 
					case
						when am.state != 'cancel' then 
							coalesce(am.total_sale_unaffected,0.00)*round(coalesce(am.currency_tc,1.00),3)
						else 0.00
					end
			end ventas_importe_operacion_inafecta,

			case 
				when am.move_type = 'out_refund' then 
					case
						when am.reversed_entry_id is not null then 
							case 
								when am.state != 'cancel' then 
									(-1.00)*coalesce(am.total_sale_igv,0.00)*round(coalesce(am2.currency_tc,1.00),3)
						
								else 0.00
							end

						else
							case 
								when am.state != 'cancel' then 
									(-1.00)*coalesce(am.total_sale_igv,0.00)*round(coalesce(am.currency_tc,1.00),3)
						
								else 0.00
							end
					end
				
				else 
					case
						when am.state != 'cancel' then 
							coalesce(am.total_sale_igv,0.00)*round(coalesce(am.currency_tc,1.00),3)
						else 0.00
					end
			end ventas_igv,

			case 
				when am.move_type = 'out_refund' then 
					case
						when am.reversed_entry_id is not null then 
							case 
								when am.state != 'cancel' then 
									(-1.00)*coalesce(am.total_venta,0.00)*round(coalesce(am2.currency_tc,1.00),3)
						
								else 0.00
							end

						else
							case 
								when am.state != 'cancel' then 
									(-1.00)*coalesce(am.total_venta,0.00)*round(coalesce(am.currency_tc,1.00),3)
						
								else 0.00
							end
					end
				
				else 
					case
						when am.state != 'cancel' then 
							coalesce(am.total_venta,0.00)*round(coalesce(am.currency_tc,1.00),3)
						else 0.00
					end
			end importe_total_comprobante,

			case 
				when am.currency_id is not null then coalesce(rc.name,'')
				else ''
			end codigo_moneda,

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
			left join l10n_latam_document_type lldt on lldt.id = am.l10n_latam_document_type_id 
			left join l10n_latam_document_type lldt2 on lldt2.id = am2.l10n_latam_document_type_id 
			left join l10n_latam_identification_type llit on llit.id = rp.l10n_latam_identification_type_id 
			where am.move_type in ('out_invoice','out_refund') and am.state in ('posted','cancel') and am.company_id = %s """%(
				self.id,
				self.company_id.id)

		return query
	##########################################################################

	"""def compute_campo_oportunidad_anotacion(self,invoice_id,tipo_comprobante,ventas_igv,ventas_valor_facturado_exportacion):
		if invoice_id:
			valor_campo=''

			if invoice_id.state not in ['cancel'] and invoice_id.date and invoice_id.invoice_date and \
				tools.getDateYYYYMM(invoice_id.date) == tools.getDateYYYYMM(invoice_id.invoice_date):
					
				if tipo_comprobante == '03':
					valor_campo='1'
				else:

					if ventas_igv==0.00:
						if ventas_valor_facturado_exportacion:
							valor_campo='1'
						else:
							valor_campo='0'

					elif ventas_igv>0.00:
						valor_campo='1'

			elif invoice_id.state not in ['cancel'] and invoice_id.date and invoice_id.invoice_date and \
				tools.getDateYYYYMM(invoice_id.date) > tools.getDateYYYYMM(invoice_id.invoice_date):
				valor_campo='8'

			elif invoice_id.state=='cancel' and invoice_id.invoice_date and self:

				anio = self.fiscal_year
				mes = self.fiscal_month
					
				if len(mes or '')==1:
					mes="0%s"%(mes)
					
				if "%s%s"%(anio,mes)==tools.getDateYYYYMM(invoice_id.invoice_date):
					valor_campo='2'

			return valor_campo

		else:
			return False"""

	###########################################################################

	def get_query_insert_into(self):

		query = """
			insert into ple_sale_line (
			ple_sale_id,
			invoice_id,
			invoice_id_2,
			asiento_contable,
			m_correlativo_asiento_contable,
			fecha_emision_comprobante,
			fecha_vencimiento,
			tipo_comprobante,
			tipo_comprobante_id,
			serie_comprobante,
			numero_comprobante,
			partner_id,
			tipo_documento_cliente,
			numero_documento_cliente,
			razon_social,
			tipo_cambio,
			ventas_valor_facturado_exportacion,
			ventas_base_imponible_operacion_gravada,
			ventas_importe_operacion_exonerada,
			ventas_importe_operacion_inafecta,
			ventas_igv,
			importe_total_comprobante,
			codigo_moneda,
			fecha_emision_original,
			tipo_comprobante_original,
			serie_comprobante_original,
			numero_comprobante_original
			)  """
		return query


	def generar_libro(self):

		self.alarm_fecha_periodo()

		registro=[]
		
		self.state='open'
		self.ple_sale_line_ids.unlink()


		query = self.get_query_ple_sale()

		filter_clause = self._get_domain()

		if filter_clause:
			query += filter_clause


		query_insert_into = self.get_query_insert_into()

		query_total = "%s %s"%(query_insert_into or '',query or '')

		self.env.cr.execute(query_total)
		
	###############################################################

	def _convert_object_date(self, date):
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''