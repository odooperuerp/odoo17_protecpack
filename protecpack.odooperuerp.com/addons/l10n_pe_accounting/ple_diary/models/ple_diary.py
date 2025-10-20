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

class PleDiary(models.Model):
	_name='ple.diary'
	_inherit='ple.base'
	_description = "Modulo PLE Libros diary"
	_rec_name='periodo_ple'

	ple_diary_line_ids=fields.One2many('ple.diary.line','ple_diary_id',
		string="Libro diary",readonly=True)


	### FILTROS DINÁMICOS
	######################### FILTROS DINAMICOS, NUEVOS CAMPOS AGREGADOS !!!
	partner_ids = fields.Many2many('res.partner','ple_diary_partner_rel','partner_id','ple_diary_id',
		string="Socios")
	options_partner=fields.Selection(selection=options,string="")

	account_ids = fields.Many2many('account.account','ple_diary_account_rel','account_id',
		'ple_diary_id',string='Cuentas')
	options_account=fields.Selection(selection=options,string="")
	
	journal_ids = fields.Many2many('account.journal','ple_diary_journal_rel','journal_id',
		'ple_diary_id',string="Diarios")
	
	options_journal=fields.Selection(selection=options,string="")

	move_ids = fields.Many2many('account.move','ple_diary_move_rel','move_id','ple_diary_id',
		string='Asientos Contables')
	
	options_move=fields.Selection(selection=options,string="")
	
	########################################################

	## BLOQUES DE IMPRESIÓN
	block_counter=fields.Integer(string="Bloque de Impresión N°" , default=0 , readonly=True)
	block_size=fields.Integer(string="Número de Registros por bloque", default=3000)
	##########################
	##buffer para asientos a apuntes

	fecha_impresion=fields.Date(string="Fecha de Impresión manual",default=datetime.now().date())
	#################################################
	fecha=fields.Boolean(string="Fecha")
	periodo=fields.Boolean(string="Periodo")

	date_from=fields.Date(string="Desde:")
	date_to=fields.Date(string="Hasta:")

	############## CHECK para indicar si se incluye o no registros anteriores no declarados
	incluir_anteriores_no_declarados = fields.Boolean(string="Incluir registros anteriores no declarados", default=False)

	fin_asiento=fields.Boolean(default=False)
	fin_documento=fields.Boolean(default=False)

	infimo=fields.Integer(default=0, string="Infimo")
	supremo=fields.Integer(default=0,string="Supremo")

	fecha_inicio= fields.Date()
	fecha_fin= fields.Date()

	periodo_ple=fields.Char(string="Periodo",compute="compute_campo_periodo",store=True)
	###############################
	_sql_constraints = [
		('fiscal_month', 'unique(fiscal_month,fiscal_year,company_id)',  'Este periodo para el PLE ya existe , revise sus registros de PLE creados!!!'),
	]
	################################################################

	@api.depends('fiscal_year','fiscal_month')
	def compute_campo_periodo(self):
		for ple in self:
			if ple.fiscal_year and ple.fiscal_month:
				ple.periodo_ple = "%s-%s-00" % (ple.fiscal_year or 'YYYY', ple.fiscal_month or 'MM') 
			else:
				ple.periodo_ple = 'Nuevo Registro'



	def open_wizard_print_form(self):
		res = super(PleDiary,self).open_wizard_print_form()

		view = self.env.ref('ple_diary.view_wizard_printer_ple_diary_form')
		if view:

			return {
				'name': _('FORMULARIO DE IMPRESIÓN DEL LIBRO PLE'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'wizard.printer.ple.diary',
				'views': [(view.id,'form')],
				'view_id': view.id,
				'target': 'new',
				'context': {
					'default_ple_diary_id': self.id,
					'default_company_id' : self.company_id.id,}}

	#################################################################
	def button_view_tree(self):	
		if self.ple_diary_line_ids:
			diccionario = {
				'name': 'Libro PLE Diario-Mayor-Simplificado',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'ple.diary.line',
				'view_id': False,
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', [i.id for i in self.ple_diary_line_ids] or [])],
				'context':{
					'search_default_filter_cuenta':1}
			}
			return diccionario
	##############################################################
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

	def unlink (self):
		for line in self:
			for line2 in line.ple_diary_line_ids:
				line2.move_line_id.write({'declared_ple_5_1_5_2_6_1':False})
			return super(PleDiary, line).unlink()

	##############################################################################

	def saldo_account_move_in_account_account(self,move_id , code_account):
		return sum(move_id.line_ids.filtered(lambda r:r.account_id.code==code_account).mapped('balance'))

	
	def account_move_account_account_totales(self):
		## creando matriz de cuentas vs asientos contables !!

		# ACTIVOS
		# PASIVOS
		# GASTOS
		# INGRESOS
		# CUENTAS DE FUNCION DEL GASTO
		asientos_totales = self.ple_diary_line_ids.mapped('move_id')

		codigo_cuentas_activos = sorted(list(self.ple_diary_line_ids.mapped('move_line_id.account_id').filtered(lambda t:t.code[0] in ['1','2','3']).mapped('code')))
		codigo_cuentas_pasivos = sorted(list(self.ple_diary_line_ids.mapped('move_line_id.account_id').filtered(lambda t:t.code[0] in ['4']).mapped('code')))
		codigo_cuentas_gastos = sorted(list(self.ple_diary_line_ids.mapped('move_line_id.account_id').filtered(lambda t:t.code[0] in ['6']).mapped('code')))
		codigo_cuentas_ingresos = sorted(list(self.ple_diary_line_ids.mapped('move_line_id.account_id').filtered(lambda t:t.code[0] in ['7']).mapped('code')))
		codigo_cuentas_funcion_gasto = sorted(list(self.ple_diary_line_ids.mapped('move_line_id.account_id').filtered(lambda t:t.code[0] in ['9']).mapped('code')))
		return [asientos_totales,codigo_cuentas_activos,codigo_cuentas_pasivos,codigo_cuentas_gastos,codigo_cuentas_ingresos,codigo_cuentas_funcion_gasto]

	##############################################################################
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
	###############################################################################

	def reinicializar_parametros_bloque(self):
		self.block_counter=0
		self.fin_asiento=False
		self.fin_documento=False
		self.infimo=0
		self.supremo=0


	def generate_tree_records(self):
		if self.identificador_libro=='050100':
			array_total=[]
			for item in self.ple_diary_line_ids:
				array_total += [(item.move_id.id,item)]

			diccionario_asientos={}
			grupos_de_asientos=groupby(sorted(array_total),lambda x:x[0])

			for k , v in grupos_de_asientos:
				self.diccionario_asientos[k]=[i[1] for i in list(v)]

	
	def get_asientos_actuales(self):
		return list(set([i.move_id for i in self.ple_diary_line_ids[self.infimo:self.supremo]]))



	def _get_current_accounts(self):
		lines = sorted(self.ple_diary_line_ids , key=lambda PleDiaryLine: (PleDiaryLine.codigo_cuenta_desagregado, PleDiaryLine.asiento_contable, PleDiaryLine.fecha_contable))
		blocks = lines[self.infimo:self.supremo]
		end = self.supremo + 1 <= len(lines) and self.supremo + 1 or (len(lines) - 1)
		if blocks[-1].codigo_cuenta_desagregado_id.id == lines[end].codigo_cuenta_desagregado_id.id:
			if blocks[-1].id != lines[end].id:
				self.supremo = list(map(lambda line: line.codigo_cuenta_desagregado_id.id, lines)).index(blocks[-1].codigo_cuenta_desagregado_id.id)
			else:
				self.supremo =  end + 1



	def criterios_impresion(self):
		res = super(PleDiary, self).criterios_impresion() or []
		res += [('codigo_cuenta_desagregado','Código Cuenta Desagregado')]
		return res


	def _action_confirm_ple(self):  
		for line in self.ple_diary_line_ids:
			if(line.move_line_id.declared_ple_5_1_5_2_6_1 != True):
				super(PleDiary , self)._action_confirm_ple('account.move.line' , line.move_line_id.id ,{'declared_ple_5_1_5_2_6_1':True})
	

	def _get_datas(self, domain):
		orden="move_id asc"
		if self.print_order == 'date':
			orden += ',date asc , account_id asc '		
		elif self.print_order == 'codigo_cuenta_desagregado':
			orden +=  ',account_id asc , date asc '		
		elif self.print_order == 'nro_documento':
			orden += ',account_id asc ,date asc '
		return self._get_query_datas('account.move.line', domain, orden)


	def _get_order_print(self , object):

		if self.print_order == 'date': # ORDENAMIENTO POR LA FECHA CONTABLE
			total=sorted(object, key=lambda PleDiaryLine:(PleDiaryLine.asiento_contable,PleDiaryLine.codigo_cuenta_desagregado,PleDiaryLine.fecha_contable))
		elif self.print_order == 'nro_documento':
			total=sorted(object , key=lambda PleDiaryLine:(PleDiaryLine.asiento_contable))
		elif self.print_order == 'codigo_cuenta_desagregado':
			total=sorted(object , key=lambda PleDiaryLine:(PleDiaryLine.asiento_contable,PleDiaryLine.fecha_contable,PleDiaryLine.codigo_cuenta_desagregado))
		return total

	#################################################
	def get_query_ple_diary(self):

		query = """
			select 
			%s as ple_diary_id,
			case
				when aml.date is not Null then TO_CHAR(aml.date,'YYYYMM00')
				else 'YYYYMM00' 
			end periodo_apunte,
			coalesce(am.name,'') as asiento_contable,
			concat('M',aml.id) as m_correlativo_asiento_contable,
			am.id as move_id,
			aml.id as move_line_id,
			aml.journal_id as journal_id, 
			aml.account_id as codigo_cuenta_desagregado_id,
			coalesce(acac.code,'') as codigo_cuenta_desagregado,
			case
				when aml.currency_id is not Null then coalesce(rc.name,'')
				when rcom.currency_id is not Null then coalesce(rc2.name,'')
			end tipo_moneda_origen,

			case
				when aml.partner_id is not Null and llit.id is not Null then coalesce(llit.l10n_pe_vat_code,'')
				else ''
			end tipo_doc_iden_emisor,

			case 
				when aml.partner_id is not null then coalesce(rp.vat,'')
				else ''
			end num_doc_iden_emisor,

			case
				when aml.l10n_latam_document_type_id is not Null then coalesce(lldt.code,'')
				else '00'
			end tipo_comprobante_pago,

			coalesce(aml.l10n_pe_prefix_code,'') as num_serie_comprobante_pago,
			coalesce(aml.l10n_pe_invoice_number,'-') as num_comprobante_pago,
			aml.date as fecha_contable,
			aml.date_maturity as fecha_vencimiento,
			aml.date as fecha_operacion,

			case 
				when am.id is not Null then coalesce(am.ref,'-')
				else coalesce(aml.name,'-')
			end glosa,

			coalesce(round(debit,2),0.00) as movimientos_debe,
			coalesce(round(credit,2),0.00) as movimientos_haber,

			case
				when '%s' <> '' and TO_CHAR(aml.date,'YYYYMMDD') >= '%s' then '1'
				else '8'
			end indicador_estado_operacion

			from account_move_line as aml 
			left join account_account acac on acac.id = aml.account_id 
			left join account_move am on am.id = aml.move_id 
			left join res_partner rp on rp.id = aml.partner_id 
			left join res_currency rc on rc.id = aml.currency_id 
			left join res_company rcom on rcom.id = aml.company_id 
			left join res_currency rc2 on rc2.id = rcom.currency_id
			left join l10n_latam_document_type lldt on lldt.id = aml.l10n_latam_document_type_id 
			left join l10n_latam_identification_type llit on llit.id = rp.l10n_latam_identification_type_id 
			where am.state in ('posted') and am.company_id = %s """%(
				self.id,
				self._periodo_fiscal() or '',
				self._periodo_fiscal() or '',
				self.company_id.id,
				)

		return query

	###########################################################################

	def _get_domain(self):

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


		filter_clause = " and aml.date >= '%s' and aml.date <= '%s' "%(
			self.fecha_inicio.strftime("%Y-%m-%d"),
			self.fecha_fin.strftime("%Y-%m-%d"))

		filter_clause += " and aml.declared_ple_5_1_5_2_6_1 is not True and aml.display_type not in ('line_section','line_note') "


		partners=tuple(self.partner_ids.mapped('id'))
		len_partners = len(partners or '')
		if len_partners:
			filter_clause += " and aml.partner_id %s %s" % (self.options_partner or 'in', str(partners) if len_partners!=1 else str(partners)[0:len(str(partners))-2] + ')')


		journals = tuple(self.journal_ids.mapped('id'))
		len_journals = len(journals or '')
		if len(self.journal_ids):
			filter_clause += " and aml.journal_id %s %s " % (self.options_journal or 'in', str(journals) if len_journals!=1 else str(journals)[0:len(str(journals))-2] + ')')


		moves = tuple(self.move_ids.mapped('id'))
		len_moves = len(moves or '')
		if len(moves):
			filter_clause += " and aml.move_id %s %s " % (self.options_move or 'in', str(moves) if len_moves!=1 else str(moves)[0:len(str(moves))-2] + ')')


		accounts = tuple(self.account_ids.mapped('id'))
		len_accounts = len(accounts or '')
		if len(self.account_ids):
			filter_clause += " and aml.account_id %s %s " % (self.options_account or 'in', str(accounts) if len_accounts!=1 else str(accounts)[0:len(str(accounts))-2] + ')')

			
		return filter_clause



	def get_query_insert_into(self):

		query = """
			insert into ple_diary_line (
				ple_diary_id,
				periodo_apunte,
				asiento_contable,
				m_correlativo_asiento_contable,
				move_id,
				move_line_id,
				journal_id,
				codigo_cuenta_desagregado_id,
				codigo_cuenta_desagregado,
				tipo_moneda_origen,
				tipo_doc_iden_emisor,
				num_doc_iden_emisor,
				tipo_comprobante_pago,
				num_serie_comprobante_pago,
				num_comprobante_pago,
				fecha_contable,
				fecha_vencimiento,
				fecha_operacion,
				glosa,
				movimientos_debe,
				movimientos_haber,
				indicador_estado_operacion
			)  """
		return query

	###############################################################################################


	def _periodo_fiscal(self):
		periodo = "%s%s00" % (self.fiscal_year or 'YYYY', self.fiscal_month or 'MM')
		return periodo



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


	################################################################3

	def generar_libro(self):

		self.alarm_fecha_periodo()

		self.state='open'
		self.ple_diary_line_ids.unlink()


		query = self.get_query_ple_diary()

		filter_clause = self._get_domain()

		if filter_clause:
			query += filter_clause


		query_insert_into = self.get_query_insert_into()

		query_total = "%s %s"%(query_insert_into or '',query or '')

		self.env.cr.execute(query_total)

	##################################################################


	def _convert_object_date(self, date):
		if date:
			return date.strftime("%d/%m/%Y")
		else:
			return ''
