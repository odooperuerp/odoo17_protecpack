import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError
import logging
from itertools import *
_logger=logging.getLogger(__name__)

options=[
	('in','esta en'),
	('not in','no esta en')
	]

class PleInventariosBalancesDetalleSaldoCuenta50EstructuraParticipacion(models.Model):
	_name='ple.inventarios.balances.3.16'
	_inherit='ple.base'
	_description = "Modulo PLE Inventarios Balances-Detalle Saldo Cuenta 50-Estructura Participación Accionaria"
	_rec_name = 'periodo_ple'

	
	ple_inventarios_balances_3_16_1_line_ids=fields.One2many('ple.inventarios.balances.3.16.1.line','ple_inventarios_balances_3_16_id',
		string="Libro Inventarios y Balances 3.16 Saldo cuenta 50",readonly=True)

	ple_inventarios_balances_3_16_2_line_ids=fields.One2many('ple.inventarios.balances.3.16.2.line','ple_inventarios_balances_3_16_id',
		string="Libro Inventarios y Balances 3.16 Estructura Participación Accionaria",readonly=True)
	

	registro_participacion_accionaria_id = fields.Many2one('shares.participations',string="Registro de Acciones y Participaciones",
		default=lambda self: self.env['shares.participations'].search([('company_id','=',self.env['res.company']._company_default_get('account.invoice').id)],limit=1),
		domain = lambda self: [('id', 'in',[i.id for i in self.env['shares.participations'].search([('company_id','=',self.env['res.company']._company_default_get('account.invoice').id)])] )],required=True)

	fecha_final=fields.Date(string="Fecha Final",required=True)

	periodo_ple=fields.Char(string="Periodo",compute="compute_campo_periodo",store=True)

	######################################################

	@api.depends('fecha_final')
	def compute_campo_periodo(self):
		for ple in self:
			if ple.fecha_final:
				ple.periodo_ple = "PLE 3.16 al %s"%(ple.fecha_final.strftime("%d/%m/%Y") or 'YYYY')

			else:
				ple.periodo_ple = 'Nuevo Registro PLE 3.16'



	def open_wizard_print_form(self):
		res = super(PleInventariosBalancesDetalleSaldoCuenta50EstructuraParticipacion,self).open_wizard_print_form()

		view = self.env.ref('ple_inventarios_balances_3_16.view_wizard_printer_ple_inventarios_balances_3_16_form')
		if view:

			return {
				'name': _('FORMULARIO DE IMPRESIÓN DEL LIBRO PLE'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'wizard.printer.ple.inventarios.balances.3.16',
				'views': [(view.id,'form')],
				'view_id': view.id,
				'target': 'new',
				'context': {
					'default_ple_inventarios_balances_3_16_line_id': self.id,
					'default_company_id' : self.company_id.id,}}

	################################################################################

	def name_get(self):
		result = []
		for ple in self:
			result.append((ple.id,"%s"%(self._convert_object_date(ple.fecha_final)) or 'New'))
		return result


	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		recs = self.search([('fecha_final', operator, name)] + args, limit=limit)
		return recs.name_get()
	##########################################################


	def query_PLE_3_16_1(self):
		query_total = """
			select 
				sum(spl.numero_acciones) as numero_acciones_totales 
			from shares_participations sp 
			join shares_participations_line spl on spl.shares_participations_id = sp.id
			where (spl.periodo_incorporacion<='%s') and
			sp.id = %s and company_id = %s""" %(
				self.fecha_final,
				self.registro_participacion_accionaria_id.id,
				self.company_id.id)
		
		return query_total



	def query_PLE_3_16_2(self):
		query_total = """
			select 
				spl.tipo_documento_socio_accionista, 
				spl.numero_documento_socio_accionista,
				spl.tipo_accion, 
				spl.codigo_tipo_accion, 
				spl.razon_social_socio_accionista, 
				spl.numero_acciones 
			from shares_participations sp 
			join shares_participations_line spl on spl.shares_participations_id = sp.id
			where (spl.periodo_incorporacion<='%s') and
			sp.id = %s and company_id = %s""" %(
				self.fecha_final, 
				self.registro_participacion_accionaria_id.id,
				self.company_id.id)
		return query_total
	########################################################

	def _periodo_fiscal(self):
		periodo = "%s%s00" % (self.fiscal_year or 'YYYY', self.fiscal_month or 'MM')
		return periodo



	def generar_libro(self):
		self.state='open'
		self.ple_inventarios_balances_3_16_1_line_ids.unlink()
		self.ple_inventarios_balances_3_16_2_line_ids.unlink()

		registro_1=[]
		registro_2=[]

		query_1=self.query_PLE_3_16_1()
		query_2=self.query_PLE_3_16_2()

		#################################################
		self.env.cr.execute(query_1)
		records_1 = self.env.cr.dictfetchall()

		for line in records_1:
			registro_1.append((0,0,{
				'periodo':self.fecha_final.strftime('%Y%m%d'),
				'importe_capital_social_participaciones':(line['numero_acciones_totales'] or 0.00)*(self.registro_participacion_accionaria_id.valor_nominal_por_accion_participacion or 0.00),
				'valor_nominal_por_accion':self.registro_participacion_accionaria_id.valor_nominal_por_accion_participacion or 0.00,
				'numero_acciones_participaciones_sociales':line['numero_acciones_totales'] or 0.00,
				'numero_acciones_participaciones_sociales_pagadas':line['numero_acciones_totales'] or 0.00
			}))

		self.ple_inventarios_balances_3_16_1_line_ids = registro_1

		################################################
		self.env.cr.execute(query_2)
		records_2 = self.env.cr.dictfetchall()

		for line in records_2:
			registro_2.append((0,0,{
				'periodo':self.fecha_final.strftime('%Y%m%d'),
				'tipo_documento_socio_accionista':line['tipo_documento_socio_accionista'] or '',
				'numero_documento_socio_accionista':line['numero_documento_socio_accionista'] or '',
				'tipo_accion':line['tipo_accion'] or '',
				'codigo_tipo_accion':line['codigo_tipo_accion'] or '',
				'razon_social_socio_accionista':line['razon_social_socio_accionista'] or '',
				'numero_acciones':line['numero_acciones'] or 0.00
			}))

		self.ple_inventarios_balances_3_16_2_line_ids = registro_2




	def _convert_object_date(self, date):
		# parametro date que retorna un valor vacio o el foramto 01/01/2100 dia/mes/año
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''


	######################################################

	def is_menor(self,a,b):
		return a<b