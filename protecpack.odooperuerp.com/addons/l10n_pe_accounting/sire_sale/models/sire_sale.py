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
	_rec_name='periodo'
	_description = "Modulo SIRE de Ventas"

	sire_sale_line_ids=fields.One2many('sire.sale.line','sire_sale_id',string="Registros de venta-Reemplazo")

	sunat_sire_sale_line_ids = fields.One2many('sunat.sire.sale.line','sire_sale_id',string="Registros de venta-propuesta")

	sire_sale_compare_line_ids = fields.One2many('sire.sale.compare.line','sire_sale_id',string="Comparación RVIE-Sistema")


	identificador_operaciones = fields.Selection(selection=[('0','Cierre de operaciones'),('1','Empresa operativa'),('2','Cierre de libro')],
		string="Identificador de operaciones",required=True,default="1")

	identificador_libro=fields.Selection(selection='available_formats_sale_sunat', string="Identificador del Libro")

	correlativo = fields.Char(string="Correlativo")

	partner_ids = fields.Many2many('res.partner','sire_sale_partner_rel','partner_id','sire_sale_id_1' ,string="Socio")
		
	journal_ids = fields.Many2many('account.journal','sire_sale_journal_rel','journal_id','sire_sale_id_3',string="Diario")

	move_ids = fields.Many2many('account.move','sire_sale_move_rel','move_id','sire_sale_id_4',string='Asiento Contable')

	currency_ids = fields.Many2many('res.currency','sire_sale_currency_rel','currency_id','sire_sale_id_6',string="Moneda")

	##################################################################################
	partner_option=fields.Selection(selection=options , string="")
	journal_option=fields.Selection(selection=options , string="")
	move_option=fields.Selection(selection=options , string="")
	currency_option=fields.Selection(selection=options , string="")

	periodo=fields.Char(string="Periodo",compute="compute_campo_periodo",store=True)

	file_zip_reemplazo = fields.Binary(string="Archivo Reemplazo", attachment=True,readonly=True)
	name_archivo_reemplazo_zip = fields.Char(string="Nombre de Archivo zip Reemplazo")

	is_rango_dias = fields.Boolean(string="Rango de Días",default=False)

	fecha_inicio = fields.Date(string="Fecha Inicio")
	fecha_fin = fields.Date(string="Fecha Fin")
	#################################################################################

	_sql_constraints = [
		('fiscal_month', 'unique(fiscal_month,fiscal_year,correlativo,company_id)',  'Este periodo para el SIRE RVIE ya existe , revise sus registros de SIRE RVIE creados !'),
	]
	#######################################################
	
	@api.depends('fiscal_year','fiscal_month')
	def compute_campo_periodo(self):
		for sire in self:
			if sire.fiscal_year and sire.fiscal_month:
				sire.periodo = "%s-%s-00" % (sire.fiscal_year or 'YYYY', sire.fiscal_month or 'MM') 
			else:
				sire.periodo = 'Nuevo Registro'



	@api.model	
	def name_get(self):
		result = []
		for sire in self:

			result.append((sire.id, "%s%s00" % (sire.fiscal_year or 'YYYY', sire.fiscal_month or 'MM') or 'Nuevo Registro'))
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

		if not temp_access_token:
			raise UserError(_('Problemas con servicios de SUNAT!\nNo se pudo obtener el Token !'))

		self.access_token = temp_access_token

		self.state='token'



	def action_ticket(self):

		periodo_rvie = "%s%s"%(self.fiscal_year,self.fiscal_month)

		temp_ticket_propuesta = ''

		if self.is_rango_dias:
			temp_ticket_propuesta = self.obtener_ticket_propuesta_rango_dias(
				periodo_rvie,
				self.fecha_inicio.strftime("%d/%m/%Y"),
				self.fecha_fin.strftime("%d/%m/%Y"),
				self.access_token) or False

		else:
			temp_ticket_propuesta = self.obtener_ticket_propuesta(periodo_rvie,self.access_token) or False

		if not temp_ticket_propuesta:
			raise UserError(_('Problemas con servicios de SUNAT!\nNo se pudo obtener el Ticket !'))

		self.ticket_propuesta = temp_ticket_propuesta

		self.state='ticket'



	def action_consultar_archivos(self):

		periodo_rvie = "%s%s"%(self.fiscal_year,self.fiscal_month)

		self.cod_tipo_archivo_reporte = None
		self.nom_archivo_reporte = None
		self.nom_archivo_contenido = None

		datos_archivo = self.obtener_datos_archivo(periodo_rvie,self.ticket_propuesta,self.access_token)

		if not datos_archivo:
			raise UserError(_('Problemas con servicios de SUNAT!\nNo se pudo obtener datos de archivo !'))

		self.cod_tipo_archivo_reporte = datos_archivo[0]
		self.nom_archivo_reporte = datos_archivo[1]
		self.nom_archivo_contenido = datos_archivo[2]

		self.state = 'name_archivos'


	#################################################################

	def action_print_zip_reemplazo(self):
		if self.state in ['reemplazo_generado','send']:

			output = BytesIO()
			self._generate_txt_reemplazo(output)
			output.seek(0)

			zip_buffer = BytesIO()

			indicador_contenido = '1' if output else'0'

			name_archivo_reemplazo = "LE%s%s%s00140400021%s12"%(
				self.company_id.vat,
				self.fiscal_year,
				self.fiscal_month,
				indicador_contenido
				)

			self.name_archivo_reemplazo_zip = "%s.zip"%(name_archivo_reemplazo or '')

			name_archivo_reemplazo = "%s.txt"%(name_archivo_reemplazo or '')
			########################################

			with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
				zip_file.writestr(name_archivo_reemplazo,output.getvalue())

			zip_buffer.seek(0)

			self.file_zip_reemplazo = base64.b64encode(zip_buffer.getvalue())

			output.close()
			zip_buffer.close()



	def action_print(self):
		if self.state in ['propuesta_generada','reemplazo_generado','send']:
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
			('move_type','in',['out_invoice','out_refund']),
			('state','not in',['draft'])
			]

		if self.is_rango_dias:

			domain += [('date','>=',self.fecha_inicio),('date','<=',self.fecha_fin)]

		else:

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
		self.cod_tipo_archivo_reporte = None
		self.nom_archivo_reporte = None
		self.nom_archivo_contenido = None
		self.archivo_sire_propuesta = None

		self.sunat_sire_sale_line_ids.unlink()
		self.sire_sale_line_ids.unlink()
		self.sire_sale_compare_line_ids.unlink()

		self.file_zip_reemplazo = None


	######################################################################

	def query_comparation(self):

		if self.sire_sale_line_ids or self.sunat_sire_sale_line_ids:
			query = """
				select 
					sssl.fecha_emision as fecha_emision,
					sssl.tipo_documento_cp as tipo_documento_cp,
					sssl.serie_documento_cp as serie_documento_cp,
					sssl.numero_documento_cp as numero_documento_cp,
					sssl.nro_doc_identidad_cliente as nro_doc_identidad_cliente,
					sssl.razon_social as razon_social,
					sssl.total_cp as total_cp,
					sssl.moneda as moneda,
					'0' as estado_compare
				from sunat_sire_sale_line as sssl
				left join 
				sire_sale_line ssl on LPAD(ssl.tipo_comprobante,2,'0') = LPAD(sssl.tipo_documento_cp,2,'0') and
				LPAD(ssl.serie_comprobante,4,'0') = LPAD(sssl.serie_documento_cp,4,'0') and 
				LPAD(ssl.numero_comprobante,8,'0') = LPAD(sssl.numero_documento_cp,8,'0') 
				where ssl.id is NULL and sssl.sire_sale_id = %s 

				UNION

				select 
					ssl.fecha_emision_comprobante as fecha_emision,
					ssl.tipo_comprobante as tipo_documento_cp,
					ssl.serie_comprobante as serie_documento_cp,
					ssl.numero_comprobante as numero_documento_cp,
					ssl.numero_documento_cliente as nro_doc_identidad_cliente,
					ssl.razon_social as razon_social,
					ssl.importe_total_comprobante as total_cp,
					ssl.codigo_moneda as moneda,
					'1' as estado_compare
				from sire_sale_line as ssl
				left join 
				sunat_sire_sale_line sssl on LPAD(sssl.tipo_documento_cp,2,'0') = LPAD(ssl.tipo_comprobante,2,'0') and
				LPAD(sssl.serie_documento_cp,4,'0') = LPAD(ssl.serie_comprobante,4,'0') and 
				LPAD(sssl.numero_documento_cp,8,'0') = LPAD(ssl.numero_comprobante,8,'0')
				where sssl.id is NULL and ssl.sire_sale_id = %s """ % (self.id,self.id)

			return query

		else:
			return False



	def generate_comparation(self):
		if self.sire_sale_line_ids or self.sunat_sire_sale_line_ids:

			self.sire_sale_compare_line_ids.unlink()

			registro=[]

			query = self.query_comparation()
			self.env.cr.execute(query)
			records = self.env.cr.dictfetchall()

			if records:
				for line in records:

					registro.append((0,0,{
						'fecha_emision': line['fecha_emision'] or False,
						'tipo_documento_cp': line['tipo_documento_cp'] or '',
						'serie_documento_cp': line['serie_documento_cp'] or '',
						'numero_documento_cp': line['numero_documento_cp'] or '',
						'nro_doc_identidad_cliente': line['nro_doc_identidad_cliente'] or '',
						'razon_social': line['razon_social'] or '',
						'total_cp': line['total_cp'] or 0.00,
						'moneda': line['moneda'] or '',
						'estado_compare': line['estado_compare'] or '',
					}))

			self.sire_sale_compare_line_ids = registro
			#self.state = 'comparacion_generada'



	def generar_libro(self):
		registro=[]
		
		self.sire_sale_line_ids.unlink()

		records = self._get_datas(self._get_domain())

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
				'tipo_comprobante':line.l10n_latam_document_type_id and line.l10n_latam_document_type_id.code or '',
				'serie_comprobante':line.l10n_pe_prefix_code or '',
				'numero_comprobante':line.l10n_pe_invoice_number or '',
				'tipo_documento_cliente':line.partner_id and \
					line.partner_id.l10n_latam_identification_type_id and line.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '',
				'numero_documento_cliente':line.partner_id and line.partner_id.vat or '',
				'razon_social':line.partner_id and line.partner_id.name or '',
			}))

		self.sire_sale_line_ids = registro
		self.state = 'reemplazo_generado'

	######################################################################


	def generar_libro_sunat_sire(self):
		registro=[]

		self.archivo_sire_propuesta = None
		#################################################################
		periodo_rvie = "%s%s"%(self.fiscal_year,self.fiscal_month)

		self.state='propuesta_generada'
		self.sunat_sire_sale_line_ids.unlink()


		archivo_sire_propuesta_temp =self.descargar_archivo_zip_txt(
			self.nom_archivo_reporte,
			self.cod_tipo_archivo_reporte,
			self.access_token,
			periodo_rvie,
			"10",
			self.ticket_propuesta)

		if not archivo_sire_propuesta_temp:
			raise UserError(_('Problemas con servicios de SUNAT!\nNo se pudo descargar el archivo de propuesta !'))


		if archivo_sire_propuesta_temp:

			lista_registros = self.descomprimir_archivo_zip(archivo_sire_propuesta_temp,self.nom_archivo_contenido)

			for line in lista_registros[1:]:

				partes = line.split('|')

				if len(partes) == 40:
					registro.append((0,0,{
						'ruc': partes[0],
						'razon_social': partes[1],
						'periodo': partes[2],
						'car_sunat': partes[3],
						'fecha_emision': datetime.strptime(partes[4],'%d/%m/%Y').date() if partes[4] else False,
						'fecha_vencimiento': datetime.strptime(partes[5],'%d/%m/%Y').date() if partes[5] else False,
						'tipo_documento_cp': partes[6],
						'serie_documento_cp': partes[7],
						'numero_documento_cp': partes[8],
						'nro_final_rango': partes[9],
						'tipo_doc_cliente': partes[10],
						'nro_doc_identidad_cliente': partes[11],
						'razon_social': partes[12],
						'valor_fcturado_exportacion': float(partes[13] or 0.00),
						'base_imponible_grabada': float(partes[14] or 0.00),
						'descuento_base_imponible': float(partes[15] or 0.00),
						'igv': float(partes[16] or 0.00),
						'descuento_igv': float(partes[17] or 0.00),
						'monto_exonerado': float(partes[18] or 0.00),
						'monto_inafecto': float(partes[19] or 0.00),
						'isc': float(partes[20] or 0.00),
						'base_imponible_ivap': float(partes[21] or 0.00),
						'ivap': float(partes[22] or 0.00),
						'icbper': float(partes[23] or 0.00),
						'otros_tributos': float(partes[24] or 0.00),
						'total_cp': float(partes[25] or 0.00),
						'moneda': partes[26],
						'tipo_cambio': partes[27],
						'fecha_emision_doc_modificado': datetime.strptime(partes[28],'%d/%m/%Y').date() if partes[28] else False,
						'tipo_cp_modificado': partes[29],
						'serie_cp_modificado': partes[30],
						'nro_cp_modificado': partes[31],
						'id_proyecto_operadores_atribucion': partes[32],
						'tipo_nota': partes[33],
						'estado_comprobante': partes[34],
						'valor_fob_embarcado': partes[35],
						'valor_op_gratuitas': partes[36],
						'tipo_operacion': partes[37],
						'dam_cp': partes[38],
						'clu': (partes[39] or '').rstrip(),
					}))
				
				else:

					partes_reconstitution = []

					for i in range(40):
						try:
							elemento = partes[i]
							partes_reconstitution.append(elemento)
						except IndexError:
							partes_reconstitution.append(False)

					#############################################

					registro.append((0,0,{
						'ruc': partes_reconstitution[0],
						'razon_social': partes_reconstitution[1],
						'periodo': partes_reconstitution[2],
						'car_sunat': partes_reconstitution[3],
						'fecha_emision': datetime.strptime(partes_reconstitution[4],'%d/%m/%Y').date() if partes_reconstitution[4] else False,
						'fecha_vencimiento': datetime.strptime(partes_reconstitution[5],'%d/%m/%Y').date() if partes_reconstitution[5] else False,
						'tipo_documento_cp': partes_reconstitution[6],
						'serie_documento_cp': partes_reconstitution[7],
						'numero_documento_cp': partes_reconstitution[8],
						'nro_final_rango': partes_reconstitution[9],
						'tipo_doc_cliente': partes_reconstitution[10],
						'nro_doc_identidad_cliente': partes_reconstitution[11],
						'razon_social': partes_reconstitution[12],
						'valor_fcturado_exportacion': float(partes_reconstitution[13] or 0.00),
						'base_imponible_grabada': float(partes_reconstitution[14] or 0.00),
						'descuento_base_imponible': float(partes_reconstitution[15] or 0.00),
						'igv': float(partes_reconstitution[16] or 0.00),
						'descuento_igv': float(partes_reconstitution[17] or 0.00),
						'monto_exonerado': float(partes_reconstitution[18] or 0.00),
						'monto_inafecto': float(partes_reconstitution[19] or 0.00),
						'isc': float(partes_reconstitution[20] or 0.00),
						'base_imponible_ivap': float(partes_reconstitution[21] or 0.00),
						'ivap': float(partes_reconstitution[22] or 0.00),
						'icbper': float(partes_reconstitution[23] or 0.00),
						'otros_tributos': float(partes_reconstitution[24] or 0.00),
						'total_cp': float(partes_reconstitution[25] or 0.00),
						'moneda': partes_reconstitution[26],
						'tipo_cambio': partes_reconstitution[27],
						'fecha_emision_doc_modificado': datetime.strptime(partes_reconstitution[28],'%d/%m/%Y').date() if partes_reconstitution[28] else False,
						'tipo_cp_modificado': partes_reconstitution[29],
						'serie_cp_modificado': partes_reconstitution[30],
						'nro_cp_modificado': partes_reconstitution[31],
						'id_proyecto_operadores_atribucion': partes_reconstitution[32],
						'tipo_nota': partes_reconstitution[33],
						'estado_comprobante': partes_reconstitution[34],
						'valor_fob_embarcado': partes_reconstitution[35],
						'valor_op_gratuitas': partes_reconstitution[36],
						'tipo_operacion': partes_reconstitution[37],
						'dam_cp': partes_reconstitution[38],
						'clu': (partes_reconstitution[39] or '').rstrip(),
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
			escritura="%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n" % (
				self.company_id.vat or '',
				self.company_id.name or '',
				"%s%s"%(self.fiscal_year,self.fiscal_month),
				'',
				line.fecha_emision_comprobante and line.fecha_emision_comprobante.strftime("%d/%m/%Y") or '',
				line.fecha_vencimiento and line.fecha_vencimiento.strftime("%d/%m/%Y") or '',
				line.tipo_comprobante or '',
				line.serie_comprobante or '',
				line.numero_comprobante or '',
				'',
				line.tipo_documento_cliente or '',
				line.numero_documento_cliente or '',
				(line.razon_social or '').strip(),
				line.ventas_valor_facturado_exportacion or 0.00,
				line.ventas_base_imponible_operacion_gravada or 0.00,
				line.ventas_descuento_base_imponible or 0.00,
				line.ventas_igv or 0.00,
				line.ventas_descuento_igv or 0.00,
				line.ventas_importe_operacion_exonerada or 0.00,
				line.ventas_importe_operacion_inafecta or 0.00,
				line.isc or 0.00,
				line.ventas_base_imponible_arroz_pilado or 0.00,
				line.ventas_impuesto_arroz_pilado or 0.00,
				line.impuesto_consumo_bolsas_plastico or 0.00,
				line.otros_impuestos or 0.00,
				line.importe_total_comprobante or 0.00,
				line.codigo_moneda or '',
				'' if line.tipo_cambio == 1.00 else line.tipo_cambio,
				line.fecha_emision_original and line.fecha_emision_original.strftime("%d/%m/%Y") or '',
				line.tipo_comprobante_original or '',
				line.serie_comprobante_original,
				line.numero_comprobante_original or '',
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

	##############################################################################################

	def obtener_ticket_propuesta_rango_dias(self,periodo,fecha_desde,fecha_hasta,token):
		if periodo and token:
			url_1 = "https://api-sire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvie/propuesta/web/propuesta/"
			url_final="%s%s%s"%(url_1,periodo,"/exportapropuesta?fecDocumentoDesde=%s&fecDocumentoHasta=%s&codTipoArchivo=0"%(
				fecha_desde,fecha_hasta))

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
			url = "https://api-sire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionprocesosmasivos/web/masivo/consultaestadotickets?perIni=%s&perFin=%s&page=1&perPage=2000&numTicket=%s"%(
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



	def descargar_archivo_zip_txt(self,nom_archivo_reporte,cod_tipo_archivo_reporte,token,periodo,cod_proceso,num_ticket):
		if nom_archivo_reporte and token:
			url = "https://api-sire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionprocesosmasivos/web/masivo/archivoreporte?nomArchivoReporte=%s&codTipoArchivoReporte=%s&codLibro=140000&perTributario=%s&codProceso=%s&numTicket=%s"%(
				nom_archivo_reporte,
				cod_tipo_archivo_reporte or "null",
				periodo,
				cod_proceso,
				num_ticket)

			payload = {}
			autorizacion = "Bearer %s"%(token)
			headers = {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
				'Authorization': autorizacion
			}

			response = requests.request("GET", url, headers=headers, data=payload)

			_logger.info('\n\nRESPUESTA DESCARGA ARCHIVO\n\n')
			_logger.info(response)
			
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
	