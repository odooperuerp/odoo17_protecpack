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
	('09','Setiembre'),
	('10','Octubre'),
	('11','Noviembre'),
	('12','Diciembre')]

class SireBase(models.Model):
	_name='sire.base'
	_description = "Modulo base SIRE SUNAT"

	## PARA CREAR UN NUEVO sire SOLO SE REQUIERE EL AÑO Y EL MES... LOS OTROS PARAMETROS( IMPRESION Y NOMENCLATURA SOLO SIRVEN PARA IMPRIMIR)
	fiscal_year = fields.Selection(selection=[(str(num), str(num)) for num in reversed(range(2000, (datetime.now().year) + 1 ))],
		string="Año fiscal")
	fiscal_month = fields.Selection(selection=meses, string="Mes fiscal")
	
	print_format = fields.Selection(selection='available_formats' , string='Formato Impresión:',default='txt')#,
		
	print_order = fields.Selection(selection='criterios_impresion',string="Criterio impresión") 
		
	########ATRIBUTOS ADICIONALES !!!
	currency_id = fields.Many2one('res.currency' , string="Impresión en moneda:" , default=lambda self: self.env['res.company']._company_default_get('account.invoice').currency_id)#,
		
	bimonetario = fields.Boolean(string="Impresión en dos monedas?" , default=False)#, 
		
	currency_second_id = fields.Many2one('res.currency', string="Otra moneda:")#, 
		
	state = fields.Selection(selection=[('draft','Borrador'),('token','Token Generado'),('ticket','Ticket Obtenido'),
		('name_archivos','Archivos Consultados'),('propuesta_generada','Propuesta Generada'),
		('reemplazo_generado','Reemplazo Generado'),('send','Declarado')],
		readonly=True, string="Estado", default="draft")

	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain = lambda self: [('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids] )],readonly=True)
	##########################################################################################

	access_token = fields.Text(string="Token de Acceso",readonly=True)
	small_access_token = fields.Char(string="Token de Acceso",readonly=True,compute="compute_campo_small_access_token")
	ticket_propuesta = fields.Char(string="Ticket de Propuesta",readonly=True)

	cod_tipo_archivo_reporte = fields.Char(string="Código tipo archivo",readonly=True)
	nom_archivo_reporte = fields.Char(string="Nombre archivo comprimido",readonly=True)
	nom_archivo_contenido = fields.Char(string="Nombre archivo contenido",readonly=True)

	archivo_sire_propuesta = fields.Binary(string="Archivo Propuesta", attachment=True,readonly=True)

	sire_type = fields.Selection(
		selection=[('with_connection_api_sunat','Con Conexión API-SUNAT'),('without_connection_api_sunat','Sin Conexión API-SUNAT')],
		string="Tipo de Proceso",
		default="with_connection_api_sunat",
		required=True,
		)

	#############################################################

	@api.depends('access_token')
	def compute_campo_small_access_token(self):
		for rec in self:
			if rec.access_token:
				rec.small_access_token = "%s ..."%(rec.access_token[:100] or '')
			else:
				rec.small_access_token = ""

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
			'09':'SETIEMBRE',
			'10':'OCTUBRE',
			'11':'NOVIEMBRE',
			'12':'DICIEMBRE'}
		return meses[month]



	def name_get(self):
		result = []
		for sire in self:
			result.append((sire.id, sire._periodo_fiscal() or 'New'))
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
	def criterios_impresion(self):  ## LO RECOMENDABLE ES CONVERTIR ESTO A UN ARRAY !!!! 
		criterios = [
			('nro_documento','N° de registro'),
			('date','Fecha de emisión'),
			]
		return criterios

	
	
	# HOLA AVAILABLRE_FORMAT PADRE
	def available_formats(self):
		formats=[
			('xlsx','xlsx'),
			('txt','txt')]
		return formats

	# HOLA INIT_BUFFER PADRE
	def _init_buffer(self, output):
		return output



	def action_print_zip_reemplazo(self):
		return True

	# HOLA ACTION_PRINT HIJO

	def action_print(self):
		return {
			'type': 'ir.actions.act_url',
			'url': 'reports/format/{}/{}/{}'.format(self._name, self.print_format, self.id),
			'target': 'new'
		}


	##################################################33

	def action_token(self):
		return True


	def action_ticket(self):
		return True

	
	def action_consultar_archivos(self):
		return True


	def generate_comparation(self):
		return True


	def action_draft(self):
		self.state="draft"


	def action_open_sire_sunat(self):
		self.generar_libro_sunat_sire()


	def action_open(self):
		self.generar_libro()
		self.state="reemplazo_generado"
	
	def generar_libro(self):
		return True

	def generar_libro_sunat_sire(self):
		return True



	def action_send(self):
		self._action_confirm_sire()
		self.state="send"


	def _action_confirm_sire(self, objet=False, ids=False, dic={'declared_sire':True}):
		self.env[objet].browse(ids).write(dic)
		# self.env[objet].write(dic)

		# return True

	# HOLA PRINTER PADRE, retorna el buffer
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