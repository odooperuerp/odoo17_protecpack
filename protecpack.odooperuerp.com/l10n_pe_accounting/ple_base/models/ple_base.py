# -*- coding: utf-8 -*-
from io import BytesIO
import calendar
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import logging
_logger=logging.getLogger(__name__)

meses=[
	('01','Enero'),
	('02','Febrero'),
	('03','Marzo'),
	('04','Abril'),
	('05','Mayo'),
	('06','Junio'),
	('07','Julio'),
	('08','Agosto'),
	('09','Septiembre'),
	('10','Octubre'),
	('11','Noviembre'),
	('12','Diciembre')]

class PleBase(models.Model):
	_name='ple.base'
	_description = "Modulo base para el PLE Libros SUNAT"


	fiscal_year = fields.Selection(selection=[(str(num), str(num)) for num in reversed(range(2000, (datetime.now().year) + 1 ))],
		string="Año fiscal")
	fiscal_month = fields.Selection(selection=meses, string="Mes fiscal")
	
	print_format = fields.Selection(selection='available_formats' , string='Formato Impresión:',default='txt')#,
		
	print_order = fields.Selection(selection='criterios_impresion',string="Criterio impresión") 
		
	state = fields.Selection(selection=[('draft','Borrador'),('open','Abierto'),('send','Declarado')],
		readonly=True,string="Estado", default="draft")

	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain = lambda self: [('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids])],
		readonly=True)

	currency_id = fields.Many2one('res.currency',string="Impresión en moneda:",
		default=lambda self: self.env['res.company']._company_default_get('account.invoice').currency_id)


	def word_month(self,month):
		meses={
			'01':'ENERO',
			'02':'FEBRERO',
			'03':'MARZO',
			'04':'ABRIL',
			'05':'MAYO',
			'06':'JUNIO',
			'07':'JULIO',
			'08':'AGOSTO',
			'09':'SEPTIEMBRE',
			'10':'OCTUBRE',
			'11':'NOVIEMBRE',
			'12':'DICIEMBRE'}
		return meses[month]


	def open_wizard_print_form(self):
		return {}

	
	def name_get(self):
		result = []
		for ple in self:
			result.append((ple.id, ple._periodo_fiscal() or 'New'))
		return result


	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		recs = self.search([('fiscal_month', operator, name),('fiscal_year', operator, name)] + args, limit=limit)
		return recs.name_get()


	def _periodo_fiscal(self):
		periodo = "%s%s00" % (self.fiscal_year or 'YYYY', self.fiscal_month or 'MM')
		return periodo


	@api.model
	def criterios_impresion(self):
		criterios = [
			('nro_documento','N° de registro'),
			('date','Fecha de emisión'),
			]
		return criterios


	def available_formats(self):
		formats=[
			('xlsx','xlsx'),
			('txt','txt')]
		return formats


	def _init_buffer(self, output):
		return output

	
	def action_print(self):
		return {
			'type': 'ir.actions.act_url',
			'url': 'reports/format/{}/{}/{}'.format(self._name, self.print_format, self.id),
			'target': 'new'
		}

	
	def action_draft(self):
		for rec in self:
			rec.state="draft"

	
	def action_open(self):
		for rec in self:
			rec.generar_libro()
			rec.state="open"
	
	def generar_libro(self):
		for rec in self:
			return True

	
	def action_send(self):
		for rec in self:
			rec._action_confirm_ple()
			rec.state="send"

	
	def _action_confirm_ple(self, objet=False, ids=False, dic={'declared_ple':True}):
		for rec in self:
			rec.env[objet].browse(ids).write(dic)


	def document_print(self):
		output = BytesIO()
		output = self._init_buffer(output)
		output.seek(0)
		return output.read()


	def _get_star_date(self):
		fecha_inicio = "%s-%s-01" %(self.fiscal_year, self.fiscal_month)
		return fecha_inicio


	def _get_end_date(self):
		fecha_fin = "%s-%s-%s" %(self.fiscal_year, self.fiscal_month, calendar.monthrange(int(self.fiscal_year),int(self.fiscal_month))[1])
		return fecha_fin


	def _get_query_datas(self, objet=False, domain=[], order_by=''):
		domain +=  [('company_id','in',[self.company_id.id])]
		return self.env[objet].search(domain + [('company_id','=',self.company_id.id)],order=order_by)