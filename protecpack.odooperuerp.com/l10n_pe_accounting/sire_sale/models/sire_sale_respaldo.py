import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError

import requests
import json
import zipfile
import io
import base64

import logging
_logger=logging.getLogger(__name__)

options=[
	('in','esta en'),
	('not in','no esta en')
	]

color_red='#F90620'
color_green='#0FEC37'


class SireSale(models.Model):
	_name='sire.sale'
	_inherit='sire.base'
	_description = "Modulo SIRE de Ventas"

	sire_sale_line_ids=fields.One2many('sire.sale.line','sire_sale_id',string="Registros de venta-Reemplazo")

	sunat_sire_sale_line_ids = fields.One2many('sunat.sire.sale.line','sire_sale_id',string="Registros de venta-propuesta")

	identificador_operaciones = fields.Selection(selection=[('0','Cierre de operaciones'),('1','Empresa operativa'),('2','Cierre de libro')],
		string="Identificador de operaciones",required=True,default="1")

	identificador_libro=fields.Selection(selection='available_formats_sale_sunat', string="Identificador del Libro")

	correlativo = fields.Char(string="Correlativo")
	partner_ids = fields.Many2many('res.partner','sire_sale_partner_rel','partner_id','sire_sale_id_1' ,string="Socio" ,readonly=True , states={'draft': [('readonly', False)]})
	journal_ids = fields.Many2many('account.journal','sire_sale_journal_rel','journal_id','sire_sale_id_3',string="Diario" ,readonly=True , states={'draft': [('readonly', False)]})
	move_ids = fields.Many2many('account.move','sire_sale_move_rel','move_id','sire_sale_id_4',string='Asiento Contable' ,readonly=True , states={'draft': [('readonly', False)]})
	currency_ids = fields.Many2many('res.currency','sire_sale_currency_rel','currency_id','sire_sale_id_6', string="Moneda" ,readonly=True , states={'draft': [('readonly', False)]})

	##################################################################################
	partner_option=fields.Selection(selection=options , string="",readonly=True , states={'draft': [('readonly', False)]})
	journal_option=fields.Selection(selection=options , string="",readonly=True , states={'draft': [('readonly', False)]})
	move_option=fields.Selection(selection=options , string="",readonly=True , states={'draft': [('readonly', False)]})
	currency_option=fields.Selection(selection=options , string="",readonly=True , states={'draft': [('readonly', False)]})

	periodo=fields.Boolean(string="Periodo" ,readonly=True , states={'draft': [('readonly', False)]})

	file_zip_reemplazo = fields.Binary(string="Archivo Reemplazo", attachment=True,readonly=True)

	fecha_inicio=''
	fecha_fin=''
	#################################################################################

	_sql_constraints = [
		('fiscal_month', 'unique(fiscal_month,fiscal_year,correlativo,company_id)',  'Este periodo para el sire ya existe , revise sus registros de sire creados !'),
	]


	#######################################################
	
	access_token = fields.Text(string="Token Generado")

	#######################################################

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




	def unlink (self):
		for line in self:
			for line2 in line.sire_sale_line_ids:
				line2.invoice_id.write({'declared_sire':False})
			return super(SireSale, line).unlink()


	#############################################################
	def action_token(self):
		temp_access_token = self.obtener_token() or False

		if temp_access_token:
			raise UserError(_('No se pudo obtener el Token !'))

		self.access_token = temp_access_token



	def action_ticket(self):
		temp_ticket_propuesta = self.obtener_ticket_propuesta(periodo_rvie,self.access_token) or False

		if not temp_ticket_propuesta:
			raise UserError(_('No se pudo obtener el Ticket !'))

		self.ticket_propuesta = temp_ticket_propuesta



	def action_print_zip_reemplazo(self):
		if self.state in ['open','send']:

			output = BytesIO()
			self._generate_txt_reemplazo(output)
			output.seek(0)

			name_archivo_reemplazo = "LE%s%s%s0014040002OIM2.TXT"%(self.company_id.vat,self.fiscal_year,self.fiscal_month)
			########################################

			zip_buffer = BytesIO()

			with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
				zip_file.writestr(name_archivo_reemplazo,output.getvalue())

			zip_buffer.seek(0)

			self.file_zip_reemplazo = base64.b64encode(zip_buffer.getvalue())

			output.close()
			zip_buffer.close()




	def action_print(self):
		if self.state in ['open','send']:
			return super(SireSale , self).action_print()
		


	def available_formats_sale_sunat(self):
		formats=[
			('03','Anexo 03: Reemplaza/Compara'),
			('04','Anexo 04: Ajustes Posteriores'),
			('05','Anexo 05: Ajustes Posteriores PLE')
			]
		return formats



	def criterios_impresion(self):
		res = super(SireSale, self).criterios_impresion() or []
		res += [('invoice_number',u'N° de documento'),('num_serie',u'N° de serie'),('table10_id','Tipo de documento')]
		return res



	def _action_confirm_sire(self):
		array_id=[]
		for line in self.sire_sale_line_ids :
			array_id.append(line.invoice_id.id)
		super(SireSale ,self)._action_confirm_sire('account.move' ,array_id,{'declared_sire':True})




	def _get_datas(self, domain):		
		return self._get_query_datas('account.move', domain, "invoice_date asc , name asc")


	##############################################


	def _get_domain(self):

		domain = [
			('type','in',['out_invoice','out_refund']),
			('state','not in',['draft'])
			]


		self.fecha_inicio= self._get_star_date()
		self.fecha_fin= self._get_end_date()
		domain += [('date','>=',self.fecha_inicio),('date','<=',self.fecha_fin)]


		partners=tuple(self.partner_ids.mapped('id'))
		len_partners = len(partners or '')
		if len_partners:
			domain.append(('partner_id',self.partner_option or 'in', partners))


		journals = tuple(self.journal_ids.mapped('id'))
		len_journals = len(journals or '')
		if len(self.journal_ids):
			domain.append(('journal_id',self.journal_option or 'in', journals))


		moves = tuple(self.move_ids.mapped('id'))
		len_moves = len(moves or '')
		if len(moves):
			domain.append(('move_id',self.move_option or 'in', moves))


		currencys = tuple(self.currency_ids.mapped('id'))
		len_currencys = len(currencys or '')
		if len(currencys):
			domain.append(('currency_id',self.currency_option or 'in', currencys))
			
		return domain



	def file_name(self, file_format):

		return self.nom_archivo_contenido




	def action_draft(self):
		super(SireSale, self).action_draft()
		
		self.access_token = None
		self.ticket_propuesta = None
		self.nom_archivo_reporte = None
		self.nom_archivo_contenido = None
		self.archivo_sire_propuesta = None

		self.sunat_sire_sale_line_ids.unlink()
		self.sire_sale_line_ids.unlink()

		self.file_zip_reemplazo = None





	def generar_libro(self):
		registro=[]
		
		self.sire_sale_line_ids.unlink()

		records = self._get_datas(self._get_domain())
		_logger.info('\n\nCONJUNTO DE REGISTROS\n\n')
		_logger.info(records)

		for line in records:

			serie = ''
			correlativo = ''

			number = line.name.split('-')
			if len(number or '')==2:
				serie = number[0]
				correlativo = number[1]

			registro.append((0,0,{
				'invoice_id':line.id,
				'fecha_emision_comprobante':line.invoice_date or None,
				'fecha_vencimiento':line.invoice_date_due or None,
				'tipo_comprobante':line.journal_id and line.journal_id.invoice_type_code_id or '',
				'serie_comprobante':serie or '',
				'numero_comprobante':correlativo or '',
				'tipo_documento_cliente':line.partner_id and \
					line.partner_id.l10n_latam_identification_type_id and line.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '',
				'numero_documento_cliente':line.partner_id and line.partner_id.vat or '',
				'razon_social':line.partner_id and line.partner_id.name or '',
				#'alert':color_red if line.state=='cancel' else color_green,
			}))

		self.sire_sale_line_ids = registro


	######################################################################



	def generar_libro_sunat_sire(self):
		registro=[]

		self.access_token = None
		self.ticket_propuesta = None
		self.nom_archivo_reporte = None
		self.nom_archivo_contenido = None
		self.archivo_sire_propuesta = None
		#################################################################
		self.state='open'
		self.sunat_sire_sale_line_ids.unlink()

		self.access_token = self.obtener_token()

		_logger.info('\n\nACCESS TOKEN\n\n')
		_logger.info(self.access_token)

		if not self.access_token:
			raise UserError(_('No se pudo obtener el Token !'))


		periodo_rvie = "%s%s"%(self.fiscal_year,self.fiscal_month)

		_logger.info('\n\nPERIODO\n\n')
		_logger.info(periodo_rvie)

		self.ticket_propuesta = self.obtener_ticket_propuesta(periodo_rvie,self.access_token)

		_logger.info('\n\nTICKET PROPUESTA\n\n')
		_logger.info(self.ticket_propuesta)

		if not self.ticket_propuesta:
			raise UserError(_('No se pudo obtener el Ticket !'))


		datos_archivo = self.obtener_datos_archivo(periodo_rvie,self.ticket_propuesta,self.access_token)

		if not datos_archivo:
			raise UserError(_('No se pudo obtener datos de archivo !'))

		self.nom_archivo_reporte = datos_archivo[1]

		self.nom_archivo_contenido = datos_archivo[2]

		archivo_sire_propuesta_temp =self.descargar_archivo_zip_txt(datos_archivo[1],datos_archivo[0],self.access_token)

		if archivo_sire_propuesta_temp:

			lista_registros = self.descomprimir_archivo_zip(archivo_sire_propuesta_temp,datos_archivo[2])
			#.archivo_sire_propuesta = base64.encodebytes(archivo_sire_propuesta_temp.encode('utf-8'))


			for line in lista_registros[1:]:

				partes = line.split('|')

				registro.append((0,0,{

					'fecha_emision': partes[0],
					'fecha_vencimiento': partes[1],
					'tipo_documento_cp': partes[2],
					'serie_documento_cp': partes[3],
					'numero_documento_cp': partes[4],
					'nro_final_rango': partes[5],
					'tipo_doc_cliente': partes[6],
					'nro_doc_identidad_cliente': partes[7],
					'razon_social': partes[8],
					'valor_fcturado_exportacion': partes[9],
					'base_imponible_grabada': partes[10],
					'descuento_base_imponible': partes[11],
					'igv': partes[12],
					'descuento_igv': partes[13],
					'monto_exonerado': partes[14],
					'monto_inafecto': partes[15],
					'isc': partes[16],
					'base_imponible_ivap': partes[17],
					'ivap': partes[18],
					'icbper': partes[19],
					'otros_tributos': partes[20],
					'total_cp': partes[21],
					'moneda': partes[22],
					'tipo_cambio': partes[23],
					'fecha_emision_doc_modificado': partes[24],
					'tipo_cp_modificado': partes[25],
					'serie_cp_modificado': partes[26],
					'nro_cp_modificado': partes[27],
					'id_proyecto_operadores_atribucion': partes[28],
					'tipo_nota': partes[29],
					'estado_comprobante': partes[30],
					'valor_fob_embarcado': partes[31],
					'valor_op_gratuitas': partes[32],
					'tipo_operacion': partes[33],
					'dam_cp': partes[34],
					'clu': partes[35],
					'car_sunat': (partes[36] or '').rstrip(),
				}))

		self.sunat_sire_sale_line_ids = registro




	def _init_buffer(self,output):

		if self.print_format == 'txt':
			self._generate_txt_propuesta(output)
		return output




	def _generate_txt_propuesta(self, output):

		for line in self.sunat_sire_sale_line_ids:
			escritura="%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n" % (
				line.fecha_emision,
				line.fecha_vencimiento,
				line.tipo_documento_cp,
				line.serie_documento_cp,
				line.numero_documento_cp,
				line.nro_final_rango,
				line.tipo_doc_cliente,
				line.nro_doc_identidad_cliente,
				line.razon_social,
				line.valor_fcturado_exportacion,
				line.base_imponible_grabada,
				line.descuento_base_imponible,
				line.igv,
				line.descuento_igv,
				line.monto_exonerado,
				line.monto_inafecto,
				line.isc,
				line.base_imponible_ivap,
				line.ivap,
				line.icbper,
				line.otros_tributos,
				line.total_cp,
				line.moneda,
				line.tipo_cambio,
				line.fecha_emision_doc_modificado,
				line.tipo_cp_modificado,
				line.serie_cp_modificado,
				line.nro_cp_modificado,
				line.id_proyecto_operadores_atribucion,
				line.tipo_nota,
				line.estado_comprobante,
				line.valor_fob_embarcado,
				line.valor_op_gratuitas,
				line.tipo_operacion,
				line.dam_cp,
				line.clu,
				(line.car_sunat or '').rstrip()
				)
			output.write(escritura.encode())
	################################################################################################################



	def _generate_txt_reemplazo(self, output):

		for line in self.sire_sale_line_ids:
			escritura="%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n" % (
				self.company_id.vat or '',
				self.company_id.name or '',
				"%s%s"%(self.fiscal_year,self.fiscal_month),
				line.fecha_emision_comprobante or '',
				line.fecha_vencimiento or '',
				line.tipo_comprobante or '',
				line.serie_comprobante or '',
				line.numero_comprobante or '',
				'',
				line.tipo_documento_cliente or '',
				line.numero_documento_cliente or '',
				line.razon_social or '',
				line.ventas_valor_facturado_exportacion or 0.0,
				line.ventas_base_imponible_operacion_gravada or 0.0,
				line.ventas_descuento_base_imponible or 0.0,
				line.ventas_igv or 0.0,
				line.ventas_descuento_igv or 0.0,
				line.ventas_importe_operacion_exonerada or 0.0,
				line.ventas_importe_operacion_inafecta or 0.0,
				line.isc or 0.0,
				line.ventas_base_imponible_arroz_pilado or 0.0,
				line.ventas_impuesto_arroz_pilado or 0.0,
				line.impuesto_consumo_bolsas_plastico or 0.0,
				line.otros_impuestos or 0.0,
				line.importe_total_comprobante or 0.0,
				line.codigo_moneda or '',
				line.tipo_cambio or 0.00,
				line.fecha_emision_original or '',
				line.tipo_comprobante_original or '',
				line.serie_comprobante_original,
				line.numero_comprobante_original or '0',
				''
			)
			output.write(escritura.encode())



	def _convert_object_date(self, date):
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''

	############################################################################################ 
	
	def obtener_token(self):

		if not self.company_id.client_id_portal_sunat or not self.company_id.client_secret_portal_sunat or not self.company_id.usuario_portal_sunat or not self.company_id.clavesol_portal_sunat:
			raise UserError(_('Por favor configure las credenciales API-SUNAT SIRE !'))

		client_id = self.company_id.client_id_portal_sunat
		client_secret = self.company_id.client_secret_portal_sunat
		ruc = self.company_id.vat
		usuario = self.company_id.usuario_portal_sunat
		clavesol = self.company_id.clavesol_portal_sunat

		url1 = "https://api-seguridad.sunat.gob.pe/v1/clientessol/"
		url_final = "%s%s/oauth2/token/"%(url1,client_id)

		username = "%s%s"%(ruc,usuario)

		payload = "grant_type=password&scope=https%%3A%%2F%%2Fapi-sire.sunat.gob.pe&client_id=%s&client_secret=%s&username=%s&password=%s"%(
			client_id,client_secret,username,clavesol)


		headers = {
			'Content-Type': 'application/x-www-form-urlencoded',
			'Cookie': 'BIGipServerpool-e-plataformaunica-https=!3hiPNwz/51YQHNAg5/qxSLLY3Weh952tnMKBGAvrISwbyn6Gf8p/uIbSZxcwD2oiTi91ZjR3GafHZg==; TS019e7fc2=014dc399cb23b95460f8d41b0d0f5e664931cecb225ac8102749f38e8cf38de138dbbca285ca0be245f1c4ad7d86d011929033df40'
		}

		response = requests.request("POST", url_final, headers=headers, data=payload)
		access_token = ""

		if response.status_code == 200:
			diccionario = json.loads(response.text)
			access_token = diccionario["access_token"]
			return access_token
		else:
			return False



	def obtener_ticket_propuesta(self,periodo,token):
		if periodo and token:
			url_1 = "https://api-sire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvie/propuesta/web/propuesta/"
			url_final="%s%s%s"%(url_1,periodo,"/exportapropuesta?codTipoArchivo=0")

			payload = {}
			autorizacion = "Bearer %s"%(token)
			headers = {
				'Authorization': autorizacion,
				'Content-Type': 'application/json',
				'Accept': 'application/json'
			}

			response = requests.request("GET", url_final, headers=headers, data=payload)

			if response.status_code == 200:
				diccionario = json.loads(response.text)
				num_ticket = diccionario["numTicket"]

				return num_ticket
			else:
				return False
		else:
			return False



	def obtener_datos_archivo(self,periodo,num_ticket,token):

		if periodo and num_ticket and token:
			url = "https://api-sire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionprocesosmasivos/web/masivo/consultaestadotickets?perIni=%s&perFin=%s&page=1&perPage=200000&numTicket=%s"%(
				periodo,periodo,num_ticket)

			payload = {}
			autorizacion = "Bearer %s"%(token)
			headers = {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
				'Authorization': autorizacion
			}

			response = requests.request("GET", url, headers=headers, data=payload)

			if response.status_code == 200:
				diccionario = json.loads(response.text)
				_logger.info('\n\nDICCIONARIO DE DATOS DE ARCHIVOS\n\n')
				_logger.info(diccionario)

				if "registros" in diccionario:
					if "archivoReporte" in diccionario["registros"][0]:

						if diccionario["registros"][0]["archivoReporte"]:
							datos_archivos = diccionario["registros"][0]["archivoReporte"][0]

							cod_tipo_archivo_reporte = datos_archivos["codTipoAchivoReporte"]
							nom_archivo_reporte = datos_archivos["nomArchivoReporte"]
							nom_archivo_contenido = datos_archivos["nomArchivoContenido"]

							return [cod_tipo_archivo_reporte,nom_archivo_reporte,nom_archivo_contenido]
						else:
							return False

					else:
						return False
				else:
					return False


			else:
				return False
		else:
			return False



	def descargar_archivo_zip_txt(self,nom_archivo_reporte,cod_tipo_archivo_reporte,token):
		if nom_archivo_reporte and token:
			url = "https://api-sire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionprocesosmasivos/web/masivo/archivoreporte?nomArchivoReporte=%s&codTipoArchivoReporte=%s&codLibro=140000"%(
				nom_archivo_reporte,cod_tipo_archivo_reporte or "null")

			payload = {}
			autorizacion = "Bearer %s"%(token)
			headers = {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
				'Authorization': autorizacion
			}

			response = requests.request("GET", url, headers=headers, data=payload)

			if response.status_code == 200:
				archivo = response.content
				
				return archivo
				#return archivo_final


			else:
				return False
		else:
			return False



	def descomprimir_archivo_zip(self,archivo_binario,nombre_archivo_txt_comprimido):

		records = []

		if archivo_binario and nombre_archivo_txt_comprimido:

			bytes_io = io.BytesIO(archivo_binario)

			with zipfile.ZipFile(bytes_io, 'r') as zip_ref:
				file_names = zip_ref.namelist()

				if file_names:
					first_file_name = file_names[0]

					with zip_ref.open(first_file_name) as file_in_zip:
						# Lee y muestra el contenido del archivo
						#text_content = file_in_zip.read()
						#print(text_content.decode('utf-8'))
						with io.TextIOWrapper(file_in_zip, encoding='utf-8') as text_file:
							for line in text_file:
								records.append(line)

		return records


	#######################################################

	meses={
	'01':'Enero',
	'02':'Febrero',
	'03':'Marzo',
	'04':'Abril',
	'05':'Mayo',
	'06':'Junio',
	'07':'Julio',
	'08':'Agosto',
	'09':'Septiembre',
	'10':'Octubre',
	'11':'Noviembre',
	'12':'Diciembre'
	}

	def _convert_currency(self, inv, valor):
		amount = valor
		if inv.currency_id and inv.company_id and inv.currency_id != inv.company_id.currency_id:
			currency_id = inv.currency_id
			amount = currency_id._convert(valor, inv.company_id.currency_id, inv.company_id, inv.invoice_date or inv.date)
		return amount


	def _data_sire_sale_head(self):
		users = self.env['res.users'].browse(self._uid)
		return [self.meses[self.fiscal_month] , self.fiscal_year , users.company_id.vat or '' , users.company_id.name or '', users.company_id.currency_id.name or '']


	