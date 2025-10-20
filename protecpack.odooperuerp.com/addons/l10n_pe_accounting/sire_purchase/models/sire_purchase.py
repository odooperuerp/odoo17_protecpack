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


class SirePurchase(models.Model):
	_name='sire.purchase'
	_inherit='sire.base'
	_rec_name='periodo'
	_description = "Modulo SIRE de Compras"

	sire_purchase_line_ids=fields.One2many('sire.purchase.line','sire_purchase_id',string="Registros de compras-Reemplazo")

	sunat_sire_purchase_line_ids = fields.One2many('sunat.sire.purchase.line','sire_purchase_id',
		string="Registros de compras-propuesta")

	sire_purchase_compare_line_ids = fields.One2many('sire.purchase.compare.line','sire_purchase_id',
		string="Comparación RCE-Sistema")

	sire_purchase_no_domiciliados_line_ids = fields.One2many('sire.purchase.no.domiciliado.line','sire_purchase_id',
		string="Registros de compras-No domiciliados")

	identificador_operaciones = fields.Selection(selection=[('0','Cierre de operaciones'),('1','Empresa operativa'),('2','Cierre de libro')],
		string="Identificador de operaciones",required=True,default="1")

	identificador_libro=fields.Selection(selection='available_formats_purchase_sunat', string="Identificador del Libro")

	correlativo = fields.Char(string="Correlativo")
	partner_ids = fields.Many2many('res.partner','sire_purchase_partner_rel','partner_id','sire_purchase_id_1' ,string="Socio")
	journal_ids = fields.Many2many('account.journal','sire_purchase_journal_rel','journal_id','sire_purchase_id_3',string="Diario")
	move_ids = fields.Many2many('account.move','sire_purchase_move_rel','move_id','sire_purchase_id_4',string='Asiento Contable')
	currency_ids = fields.Many2many('res.currency','sire_purchase_currency_rel','currency_id','sire_purchase_id_6', string="Moneda")

	##################################################################################
	partner_option=fields.Selection(selection=options , string="")
	journal_option=fields.Selection(selection=options , string="")
	move_option=fields.Selection(selection=options , string="")
	currency_option=fields.Selection(selection=options , string="")

	periodo=fields.Char(string="Periodo",compute="compute_campo_periodo",store=True)

	file_zip_reemplazo = fields.Binary(string="Archivo Reemplazo", attachment=True,readonly=True)
	file_zip_no_domiciliados = fields.Binary(string="Archivo no domiciliados", attachment=True,readonly=True)


	is_rango_dias = fields.Boolean(string="Rango de Días",default=False)

	fecha_inicio = fields.Date(string="Fecha Inicio")
	fecha_fin = fields.Date(string="Fecha Fin")
	
	#################################################################################
	name_archivo_reemplazo_domiciliado_zip = fields.Char(string="Nombre de archivo zip reemplazo Domiciliado")
	name_archivo_no_domiciliado_zip = fields.Char(string="Nombre de archivo zip No Domiciliado")
	##################################################################################

	_sql_constraints = [
		('fiscal_month', 'unique(fiscal_month,fiscal_year,correlativo,company_id)',  'Este periodo para el sire ya existe , revise sus registros de sire creados !'),
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
			for line2 in line.sire_purchase_line_ids:
				line2.invoice_id.write({'declared_sire':False})
			return super(SirePurchase, line).unlink()


	#############################################################
	def action_token(self):
		temp_access_token = self.obtener_token() or False

		if not temp_access_token:
			raise UserError(_('Problemas con servicios de SUNAT!\nNo se pudo obtener el Token !'))

		self.access_token = temp_access_token

		self.state='token'

	
	##############################################################

	def action_ticket(self):

		periodo_rce = "%s%s"%(self.fiscal_year,self.fiscal_month)

		temp_ticket_propuesta = ''

		if self.is_rango_dias:
			temp_ticket_propuesta = self.obtener_ticket_propuesta_rango_dias(
				periodo_rce,
				self.fecha_inicio.strftime("%Y-%m-%d"),
				self.fecha_fin.strftime("%Y-%m-%d"),
				self.access_token) or False

		else:
			temp_ticket_propuesta = self.obtener_ticket_propuesta(periodo_rce,self.access_token) or False

		if not temp_ticket_propuesta:
			raise UserError(_('Problemas con servicios de SUNAT!\nNo se pudo obtener el Ticket !'))

		self.ticket_propuesta = temp_ticket_propuesta

		self.state='ticket'

	##############################################################
	
	def action_consultar_archivos(self):

		periodo_rce = "%s%s"%(self.fiscal_year,self.fiscal_month)

		self.cod_tipo_archivo_reporte = None
		self.nom_archivo_reporte = None
		self.nom_archivo_contenido = None

		datos_archivo = self.obtener_datos_archivo(periodo_rce,self.ticket_propuesta,self.access_token)

		if not datos_archivo:
			raise UserError(_('Problemas con servicios de SUNAT!\nNo se pudo obtener datos de archivo !'))

		self.cod_tipo_archivo_reporte = datos_archivo[0]
		self.nom_archivo_reporte = datos_archivo[1]
		self.nom_archivo_contenido = datos_archivo[2]

		self.state = 'name_archivos'


	
	def action_print_zip_reemplazo(self):

		if self.state in ['reemplazo_generado','send']:

			output = BytesIO()
			self._generate_txt_reemplazo(output)
			output.seek(0)

			zip_buffer = BytesIO()

			indicador_contenido = '1' if output else '0'

			name_archivo_reemplazo = "LE%s%s%s00080400021%s12"%(
				self.company_id.vat,
				self.fiscal_year,
				self.fiscal_month,
				indicador_contenido)

			self.name_archivo_reemplazo_domiciliado_zip = "%s.zip"%(name_archivo_reemplazo or '')

			name_archivo_reemplazo = "%s.txt"%(name_archivo_reemplazo)

			with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
				zip_file.writestr(name_archivo_reemplazo,output.getvalue())

			zip_buffer.seek(0)

			self.file_zip_reemplazo = base64.b64encode(zip_buffer.getvalue())

			output.close()
			zip_buffer.close()


	########################################################################################

	def action_print_zip_no_domiciliado(self):
		if self.state in ['reemplazo_generado','send']:

			output = BytesIO()
			self._generate_txt_no_domiciliados(output)
			output.seek(0)

			zip_buffer = BytesIO()
			indicador_contenido = '1' if zip_buffer else '0'

			name_archivo_reemplazo = "LE%s%s%s00080500001%s12"%(
				self.company_id.vat,
				self.fiscal_year,
				self.fiscal_month,
				indicador_contenido)
			#######################################################

			self.name_archivo_no_domiciliado_zip = "%s.zip"%(name_archivo_reemplazo or '')

			name_archivo_reemplazo = "%s.txt"%(name_archivo_reemplazo)

			########################################################

			with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
				zip_file.writestr(name_archivo_reemplazo,output.getvalue())

			zip_buffer.seek(0)

			self.file_zip_no_domiciliados = base64.b64encode(zip_buffer.getvalue())

			output.close()
			zip_buffer.close()


	########################################################################################

	def action_print(self):
		if self.state in ['propuesta_generada','reemplazo_generado','send']:
			return super(SirePurchase , self).action_print()
		


	def available_formats_purchase_sunat(self):
		formats=[
			('03','Anexo 03: Reemplaza/Compara'),
			('04','Anexo 04: Ajustes Posteriores'),
			('05','Anexo 05: Ajustes Posteriores PLE')
			]
		return formats


	def criterios_impresion(self):
		res = super(SirePurchase, self).criterios_impresion() or []
		res += [('invoice_number',u'N° de documento'),('num_serie',u'N° de serie'),('table10_id','Tipo de documento')]
		return res



	def _action_confirm_sire(self):
		array_id=[]
		for line in self.sire_purchase_line_ids :
			array_id.append(line.invoice_id.id)
		super(SirePurchase ,self)._action_confirm_sire('account.move' ,array_id,{'declared_sire':True})



	def _get_datas(self, domain):		
		return self._get_query_datas('account.move', domain, "invoice_date asc , name asc")

	##############################################


	def _get_domain(self):

		domain = [
			('move_type','in',['in_invoice','in_refund']),
			('state','in',['posted'])
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
		super(SirePurchase, self).action_draft()
		
		self.access_token = None
		self.ticket_propuesta = None
		self.cod_tipo_archivo_reporte = None
		self.nom_archivo_reporte = None
		self.nom_archivo_contenido = None
		self.archivo_sire_propuesta = None

		self.sunat_sire_purchase_line_ids.unlink()
		self.sire_purchase_line_ids.unlink()
		self.sire_purchase_compare_line_ids.unlink()

		self.file_zip_reemplazo = None


	######################################################################

	def query_comparation(self):
		if self.sire_purchase_line_ids or self.sunat_sire_purchase_line_ids:
			query = """
				select 
					sssl.fecha_emision as fecha_emision,
					sssl.tipo_comprobante as tipo_documento_cp,
					sssl.serie_comprobante as serie_documento_cp,
					sssl.nro_comprobante_nro_inicial as numero_documento_cp,
					sssl.num_doc_identidad_proveedor as nro_doc_identidad_proveedor,
					sssl.razon_social_proveedor as razon_social,
					sssl.total_comprobante as total_cp,
					sssl.codigo_moneda as moneda,
					'0' as estado_compare
				from sunat_sire_purchase_line as sssl
				left join 
				sire_purchase_line ssl on 
				LPAD(ssl.tipo_comprobante,2,'0') = LPAD(sssl.tipo_comprobante,2,'0') and
				LPAD(ssl.serie_comprobante,4,'0') = LPAD(sssl.serie_comprobante,4,'0') and 
				LPAD(ssl.numero_comprobante,8,'0') = LPAD(sssl.nro_comprobante_nro_inicial,8,'0') and 
				ssl.ruc_dni = sssl.num_doc_identidad_proveedor 
				where ssl.id is NULL and sssl.sire_purchase_id = %s 

				UNION

				select 
					ssl.fecha_emision_comprobante as fecha_emision,
					ssl.tipo_comprobante as tipo_documento_cp,
					ssl.serie_comprobante as serie_documento_cp,
					ssl.numero_comprobante as numero_documento_cp,
					ssl.ruc_dni as nro_doc_identidad_proveedor,
					ssl.razon_social as razon_social,
					ssl.importe_adquisiciones_registradas as total_cp,
					ssl.codigo_moneda as moneda,
					'1' as estado_compare
				from sire_purchase_line as ssl
				left join 
				sunat_sire_purchase_line sssl on LPAD(sssl.tipo_comprobante,2,'0') = LPAD(ssl.tipo_comprobante,2,'0') and
				LPAD(sssl.serie_comprobante,4,'0') = LPAD(ssl.serie_comprobante,4,'0') and 
				LPAD(sssl.nro_comprobante_nro_inicial,8,'0') = LPAD(ssl.numero_comprobante,8,'0') and 
				ssl.ruc_dni = sssl.num_doc_identidad_proveedor 
				where sssl.id is NULL and ssl.sire_purchase_id = %s""" % (self.id , self.id)

			return query

		else:
			return False



	def generate_comparation(self):
		if self.sire_purchase_line_ids or self.sunat_sire_purchase_line_ids:

			self.sire_purchase_compare_line_ids.unlink()

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
						'nro_doc_identidad_proveedor': line['nro_doc_identidad_proveedor'] or '',
						'razon_social': line['razon_social'] or '',
						'total_cp': line['total_cp'] or 0.00,
						'moneda': line['moneda'] or '',
						'estado_compare': line['estado_compare'] or '',
					}))

			self.sire_purchase_compare_line_ids = registro
			#self.state = 'comparacion_generada'

	########################################################

	def generar_libro(self):
		registro=[]
		
		self.sire_purchase_line_ids.unlink()

		records = self._get_datas(self._get_domain())

		for line in records:

			if str(line.partner_id.l10n_latam_identification_type_id and line.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '').strip() not in ['0'] and\
				(str(line.l10n_latam_document_type_id and line.l10n_latam_document_type_id.code or '').strip() not in ['91','97','98','02']):


				registro.append((0,0,{
					'invoice_id':line.id,
					'fecha_emision_comprobante':line.invoice_date or None,
					'fecha_vencimiento':line.invoice_date_due or None,
					'tipo_comprobante':line.l10n_latam_document_type_id and line.l10n_latam_document_type_id.code or '',
					'serie_comprobante':line.l10n_pe_prefix_code or '',
					'numero_comprobante':line.l10n_pe_invoice_number or '',
					'tipo_documento_proveedor':line.partner_id and \
						line.partner_id.l10n_latam_identification_type_id and line.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '',
					'ruc_dni':line.partner_id and line.partner_id.vat or '',
					'razon_social':line.partner_id and line.partner_id.name or '',
				}))

		self.sire_purchase_line_ids = registro
		self.state = 'reemplazo_generado'

	######################################################################

	def generar_libro_no_domiciliados(self):
		registro=[]
		
		self.sire_purchase_no_domiciliados_line_ids.unlink()

		records = self._get_datas(self._get_domain())

		for line in records:

			if line.l10n_latam_document_type_id and line.l10n_latam_document_type_id.code in ['91','97','98']:

				"""serie = ''
				correlativo = ''

				number = line.ref.split('-')
				if len(number or '')==2:
					serie = number[0]
					correlativo = number[1]"""

				registro.append((0,0,{
					'invoice_id':line.id,
					'fecha_emision_comprobante':line.invoice_date or None,
					'tipo_comprobante':line.l10n_latam_document_type_id and line.l10n_latam_document_type_id.code or '',
					'serie_comprobante':line.l10n_pe_prefix_code or '',
					'numero_comprobante':line.l10n_pe_invoice_number or '',
					'valor_adquisiciones': line.amount_total or 0.00,
					'numero_identificacion':line.partner_id and line.partner_id.vat or '',
					'razon_social':line.partner_id and line.partner_id.name or '',
					'modalidad_servicio_sujeto':line.sunat_table_32_id and line.sunat_table_32_id.code or '',
					'convenios_evitar_doble_imposicion':line.sunat_table_25_id and line.sunat_table_25_id.code or '',
				}))

		self.sire_purchase_no_domiciliados_line_ids = registro

	######################################################################


	def generar_libro_sunat_sire(self):
		registro=[]

		self.archivo_sire_propuesta = None
		#################################################################
		periodo_rce = "%s%s"%(self.fiscal_year,self.fiscal_month)

		self.state='propuesta_generada'
		self.sunat_sire_purchase_line_ids.unlink()

		archivo_sire_propuesta_temp =self.descargar_archivo_zip_txt(
			self.nom_archivo_reporte,
			self.cod_tipo_archivo_reporte,
			self.access_token,
			periodo_rce,
			"10",
			self.ticket_propuesta or '')

		if not archivo_sire_propuesta_temp:
			raise UserError(_('Problemas con servicios de SUNAT!\nNo se pudo descargar el archivo de propuesta !'))


		if archivo_sire_propuesta_temp:

			lista_registros = self.descomprimir_archivo_zip(archivo_sire_propuesta_temp,self.nom_archivo_contenido)

			for line in lista_registros[1:]:

				partes = (line or '').rstrip().split('|')

				if len(partes) == 80:
					registro.append((0,0,{

						'ruc': partes[0],
						'razon_social': partes[1],
						'periodo': partes[2],
						'car_sunat': partes[3],
						'fecha_emision': datetime.strptime(partes[4],'%d/%m/%Y').date() if partes[4] else False,
						'fecha_vencimiento':datetime.strptime(partes[5],'%d/%m/%Y').date() if partes[5] else False,
						'tipo_comprobante': partes[6],
						'serie_comprobante': partes[7],
						'anio_emision_dm': partes[8],
						'nro_comprobante_nro_inicial': partes[9],
						'nro_final': partes[10],
						'tipo_doc_identidad_proveedor': partes[11],
						'num_doc_identidad_proveedor': partes[12],
						'razon_social_proveedor': partes[13],
						'base_imponible_gravada': partes[14],
						'igv': partes[15],
						'base_imponible_gravada_dgng': partes[16],
						'igv_dgng': partes[17],
						'base_imponible_gravada_dng': partes[18],
						'igv_dng': partes[19],
						'valor_adquisiciones_ng': partes[20],
						'isc': partes[21],
						'icbper': partes[22],
						'otros_tributos': partes[23],
						'total_comprobante': partes[24],
						'codigo_moneda': partes[25],
						'tipo_cambio': partes[26],
						'fecha_emision_doc_modificado': datetime.strptime(partes[27],'%d/%m/%Y').date() if partes[27] else False,
						'tipo_comprobante_modificado': partes[28],
						'serie_comprobante_modificado': partes[29],
						'cod_dam': partes[30],
						'numero_comprobante_modificado': partes[31],
						'clasif_bss': partes[32],
						'id_proyecto': partes[33],
						'porcentaje_participacion': partes[34],
						'imb': partes[35],
						'car_cp_modificar': partes[36],
						'marca_detraccion': partes[37],
						'tipo_nota': partes[38],
						'estado_comprobante': partes[39],
						'inconsistencias': partes[40],
						'clu_1': partes[41],
						'clu_2': partes[42],
						'clu_3': partes[43],
						'clu_4': partes[44],
						'clu_5': partes[45],
						'clu_6': partes[46],
						'clu_7': partes[47],
						'clu_8': partes[48],
						'clu_9': partes[49],
						'clu_10': partes[50],
						'clu_11': partes[51],
						'clu_12': partes[52],
						'clu_13': partes[53],
						'clu_14': partes[54],
						'clu_15': partes[55],
						'clu_16': partes[56],
						'clu_17': partes[57],
						'clu_18': partes[58],
						'clu_19': partes[59],
						'clu_20': partes[60],
						'clu_21': partes[61],
						'clu_22': partes[62],
						'clu_23': partes[63],
						'clu_24': partes[64],
						'clu_25': partes[65],
						'clu_26': partes[66],
						'clu_27': partes[67],
						'clu_28': partes[68],
						'clu_29': partes[69],
						'clu_30': partes[70],
						'clu_31': partes[71],
						'clu_32': partes[72],
						'clu_33': partes[73],
						'clu_34': partes[74],
						'clu_35': partes[75],
						'clu_36': partes[76],
						'clu_37': partes[77],
						'clu_38': partes[78],
						'clu_39': (partes[79] or '').rstrip()
					}))

				else:

					partes_reconstitution = []

					for i in range(80):
						try:
							elemento = partes[i]
							partes_reconstitution.append(elemento)
						except IndexError:
							partes_reconstitution.append(False)

					##########################################################
					registro.append((0,0,{

						'ruc': partes_reconstitution[0],
						'razon_social': partes_reconstitution[1],
						'periodo': partes_reconstitution[2],
						'car_sunat': partes_reconstitution[3],
						'fecha_emision': datetime.strptime(partes_reconstitution[4],'%d/%m/%Y').date() if partes_reconstitution[4] else False,
						'fecha_vencimiento':datetime.strptime(partes_reconstitution[5],'%d/%m/%Y').date() if partes_reconstitution[5] else False,
						'tipo_comprobante': partes_reconstitution[6],
						'serie_comprobante': partes_reconstitution[7],
						'anio_emision_dm': partes_reconstitution[8],
						'nro_comprobante_nro_inicial': partes_reconstitution[9],
						'nro_final': partes_reconstitution[10],
						'tipo_doc_identidad_proveedor': partes_reconstitution[11],
						'num_doc_identidad_proveedor': partes_reconstitution[12],
						'razon_social_proveedor': partes_reconstitution[13],
						'base_imponible_gravada': partes_reconstitution[14],
						'igv': partes_reconstitution[15],
						'base_imponible_gravada_dgng': partes_reconstitution[16],
						'igv_dgng': partes_reconstitution[17],
						'base_imponible_gravada_dng': partes_reconstitution[18],
						'igv_dng': partes_reconstitution[19],
						'valor_adquisiciones_ng': partes_reconstitution[20],
						'isc': partes_reconstitution[21],
						'icbper': partes_reconstitution[22],
						'otros_tributos': partes_reconstitution[23],
						'total_comprobante': partes_reconstitution[24],
						'codigo_moneda': partes_reconstitution[25],
						'tipo_cambio': partes_reconstitution[26],
						'fecha_emision_doc_modificado': datetime.strptime(partes_reconstitution[27],'%d/%m/%Y').date() if partes_reconstitution[27] else False,
						'tipo_comprobante_modificado': partes_reconstitution[28],
						'serie_comprobante_modificado': partes_reconstitution[29],
						'cod_dam': partes_reconstitution[30],
						'numero_comprobante_modificado': partes_reconstitution[31],
						'clasif_bss': partes_reconstitution[32],
						'id_proyecto': partes_reconstitution[33],
						'porcentaje_participacion': partes_reconstitution[34],
						'imb': partes_reconstitution[35],
						'car_cp_modificar': partes_reconstitution[36],
						'marca_detraccion': partes_reconstitution[37],
						'tipo_nota': partes_reconstitution[38],
						'estado_comprobante': partes_reconstitution[39],
						'inconsistencias': partes_reconstitution[40],
						'clu_1': partes_reconstitution[41],
						'clu_2': partes_reconstitution[42],
						'clu_3': partes_reconstitution[43],
						'clu_4': partes_reconstitution[44],
						'clu_5': partes_reconstitution[45],
						'clu_6': partes_reconstitution[46],
						'clu_7': partes_reconstitution[47],
						'clu_8': partes_reconstitution[48],
						'clu_9': partes_reconstitution[49],
						'clu_10': partes_reconstitution[50],
						'clu_11': partes_reconstitution[51],
						'clu_12': partes_reconstitution[52],
						'clu_13': partes_reconstitution[53],
						'clu_14': partes_reconstitution[54],
						'clu_15': partes_reconstitution[55],
						'clu_16': partes_reconstitution[56],
						'clu_17': partes_reconstitution[57],
						'clu_18': partes_reconstitution[58],
						'clu_19': partes_reconstitution[59],
						'clu_20': partes_reconstitution[60],
						'clu_21': partes_reconstitution[61],
						'clu_22': partes_reconstitution[62],
						'clu_23': partes_reconstitution[63],
						'clu_24': partes_reconstitution[64],
						'clu_25': partes_reconstitution[65],
						'clu_26': partes_reconstitution[66],
						'clu_27': partes_reconstitution[67],
						'clu_28': partes_reconstitution[68],
						'clu_29': partes_reconstitution[69],
						'clu_30': partes_reconstitution[70],
						'clu_31': partes_reconstitution[71],
						'clu_32': partes_reconstitution[72],
						'clu_33': partes_reconstitution[73],
						'clu_34': partes_reconstitution[74],
						'clu_35': partes_reconstitution[75],
						'clu_36': partes_reconstitution[76],
						'clu_37': partes_reconstitution[77],
						'clu_38': partes_reconstitution[78],
						'clu_39': (partes_reconstitution[79] or '').rstrip()
					}))

		self.sunat_sire_purchase_line_ids = registro



	def _init_buffer(self,output):

		if self.print_format == 'txt':
			self._generate_txt_propuesta(output)
		return output



	def _generate_txt_propuesta(self, output):

		for line in self.sunat_sire_purchase_line_ids:
			escritura="%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n" % (

				line.ruc or '',
				line.razon_social or '',
				line.periodo or '',
				line.car_sunat or '',
				line.fecha_emision or '',
				line.fecha_vencimiento or '',
				line.tipo_comprobante or '',
				line.serie_comprobante or '',
				line.anio_emision_dm or '',
				line.nro_comprobante_nro_inicial or '',
				line.nro_final or '',
				line.tipo_doc_identidad_proveedor or '',
				line.num_doc_identidad_proveedor or '',
				line.razon_social_proveedor or '',
				line.base_imponible_gravada or 0.00,
				line.igv or 0.00,
				line.base_imponible_gravada_dgng or 0.00,
				line.igv_dgng or 0.00,
				line.base_imponible_gravada_dng or 0.00,
				line.igv_dng or 0.00,
				line.valor_adquisiciones_ng or 0.00,
				line.isc or 0.00,
				line.icbper or 0.00,
				line.otros_tributos or 0.00,
				line.total_comprobante or 0.00,
				line.codigo_moneda or '',
				line.tipo_cambio or '',
				line.fecha_emision_doc_modificado or '',
				line.tipo_comprobante_modificado or '',
				line.serie_comprobante_modificado or '',
				line.cod_dam or '',
				line.numero_comprobante_modificado or '',
				line.clasif_bss or '',
				line.id_proyecto or '',
				line.porcentaje_participacion or '',
				line.imb or '',
				line.car_cp_modificar or '',
				line.marca_detraccion or '',
				line.tipo_nota or '',
				line.estado_comprobante or '',
				line.inconsistencias or '',
				line.clu_1 or '',
				line.clu_2 or '',
				line.clu_3 or '',
				line.clu_4 or '',
				line.clu_5 or '',
				line.clu_6 or '',
				line.clu_7 or '',
				line.clu_8 or '',
				line.clu_9 or '',
				line.clu_10 or '',
				line.clu_11 or '',
				line.clu_12 or '',
				line.clu_13 or '',
				line.clu_14 or '',
				line.clu_15 or '',
				line.clu_16 or '',
				line.clu_17 or '',
				line.clu_18 or '',
				line.clu_19 or '',
				line.clu_20 or '',
				line.clu_21 or '',
				line.clu_22 or '',
				line.clu_23 or '',
				line.clu_24 or '',
				line.clu_25 or '',
				line.clu_26 or '',
				line.clu_27 or '',
				line.clu_28 or '',
				line.clu_29 or '',
				line.clu_30 or '',
				line.clu_31 or '',
				line.clu_32 or '',
				line.clu_33 or '',
				line.clu_34 or '',
				line.clu_35 or '',
				line.clu_36 or '',
				line.clu_37 or '',
				line.clu_38 or '',
				(line.clu_39 or '').rstrip(),
				)

			output.write(escritura.encode())
	################################################################################################################



	def _generate_txt_reemplazo(self, output):

		for line in self.sire_purchase_line_ids:
			escritura="%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n" % (
				self.company_id.vat or '',
				self.company_id.name or '',
				"%s%s"%(self.fiscal_year,self.fiscal_month),
				line.car or '',
				line.fecha_emision_comprobante and line.fecha_emision_comprobante.strftime("%d/%m/%Y") or '',
				line.fecha_vencimiento and line.fecha_vencimiento.strftime("%d/%m/%Y") or '',
				line.tipo_comprobante or '',
				line.serie_comprobante or '',
				line.anio_emision_DUA or '',
				line.numero_comprobante or '',
				'',
				line.tipo_documento_proveedor or '',
				line.ruc_dni or '',
				line.razon_social or '',
				#line.operaciones_sin_igv or '',
				format(line.base_imponible_igv_gravadas or 0.00,".2f"),
				format(line.monto_igv_1 or 0.00,".2f"),
				format(line.base_imponible_igv_no_gravadas or 0.00,".2f"),
				format(line.monto_igv_2 or 0.00,".2f"),
				format(line.base_imponible_no_igv or 0.00,".2f"),
				format(line.monto_igv_3 or 0.00,".2f"),
				format(line.valor_no_gravadas or 0.00,".2f"),
				format(line.isc or 0.00,".2f"),
				format(line.impuesto_consumo_bolsas_plastico or 0.00,".2f"),
				format(line.otros_impuestos or 0.00,".2f"),
				format(line.importe_adquisiciones_registradas or 0.00,".2f"),
				line.codigo_moneda or '',
				'' if line.tipo_cambio == 1.00 else format(line.tipo_cambio or 1.000,".3f"),
				line.fecha_emision_original and line.fecha_emision_original.strftime("%d/%m/%Y") or '',
				line.tipo_comprobante_original or '',
				line.serie_comprobante_original or '',
				line.dua_doc_modificado or '',
				line.numero_comprobante_original or '',
				line.clasificacion_bienes or '',
				line.identificacion_contrato or '',
				line.participacion_contrato or '',
				line.imp_mat_beneficio or '',
				line.indicador_exclusion_inclusion or '',
				'',
				'',
				'',
				'',
			)
			output.write(escritura.encode())

	###########################################################################################

	def _generate_txt_no_domiciliados(self, output):

		for line in self.sire_purchase_no_domiciliados_line_ids:
			escritura="%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n" % (

				"%s%s"%(self.fiscal_year,self.fiscal_month),
				'',
				line.fecha_emision_comprobante and line.fecha_emision_comprobante.strftime("%d/%m/%Y") or '',
				line.tipo_comprobante or '',
				line.serie_comprobante or '',
				line.numero_comprobante or '',
				line.valor_adquisiciones or '',
				line.otros_conceptos_adicionales or '',
				line.importe_total or '',
				line.tipo_comprobante_credito_fiscal or '',
				line.serie_comprobante_credito_fiscal or '',
				line.anio_emision_DUA or '',
				line.numero_comprobante_pago_impuesto or '0',
				line.retencion_igv or 0.00,
				line.codigo_moneda or '',
				line.tipo_cambio or '',
				line.pais_residencia or '',
				line.razon_social or '',
				line.domicilio_extranjero or '',
				line.numero_identificacion or '',
				line.identificacion_beneficiario or '',
				line.razon_social_beneficiario or '',
				line.pais_beneficiario or '',
				line.vinculo_sujeto_beneficiario or '00',
				line.renta_bruta or 0.00,
				line.deduccion_costo_capital or 0.00,
				line.renta_neta or 0.00,
				line.tasa_retencion or 0.00,
				line.impuesto_retenido or 0.00,
				line.convenios_evitar_doble_imposicion or '00',
				line.exoneracion_aplicada or '',
				line.tipo_renta or '',
				line.modalidad_servicio_sujeto or '',
				line.aplicacion_ley_impuesto_renta or '',
				line.car or '',
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
			url_1 = "https://api-sire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/propuesta/"
			url_final="%s/%s/exportacioncomprobantepropuesta?codTipoArchivo=0&codOrigenEnvio=1&fecEmisionIni=%s&fecEmisionFin=%s&codTipoCDP=01"%(
				url_1,periodo,
				self._get_star_date(),
				self._get_end_date())

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

	######################################################################################################

	def obtener_ticket_propuesta_rango_dias(self,periodo,fecha_desde,fecha_hasta,token):
		if periodo and token:

			url_1 = "https://api-sire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/propuesta/"
			url_final="%s/%s/exportacioncomprobantepropuesta?codTipoArchivo=0&codOrigenEnvio=1&fecEmisionIni=%s&fecEmisionFin=%s&codTipoCDP=01"%(
				url_1,
				periodo,
				fecha_desde,
				fecha_hasta)

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




	#######################################################################################################
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

	##########################################################################################################################

	"""def descargar_archivo_zip_txt(self,periodo,token):
		if periodo and token:
			url_1 = "https://api-sire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/propuesta/"
			url_final="%s/%s/exportacioncomprobantepropuesta?codTipoArchivo=0&codOrigenEnvio=1&fecEmisionIni=%s&fecEmisionFin=%s&codTipoCDP=01"%(
				url_1,periodo,
				self._get_star_date(),
				self._get_end_date())

			payload = {}
			autorizacion = "Bearer %s"%(token)
			headers = {
				'Authorization': autorizacion,
				'Content-Type': 'application/json',
				'Accept': 'application/json'
			}

			response = requests.request("GET", url_final, headers=headers, data=payload)

			if response.status_code == 200:
				_logger.info('\n\nRESPUESTA TICKET\n\n')
				_logger.info(response.text)
				archivo = response.content

				return archivo

			else:
				return False
		
		else:
			return False """

	####################################################################################################################

	def descargar_archivo_zip_txt(self,nom_archivo_reporte,cod_tipo_archivo_reporte,token,periodo,cod_proceso,num_ticket):
		if nom_archivo_reporte and token:
			url = "https://api-sire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionprocesosmasivos/web/masivo/archivoreporte?nomArchivoReporte=%s&codTipoArchivoReporte=%s&perTributario=%s&codProceso=%s&numTicket=%s"%(
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

			if response.status_code == 200:
				archivo = response.content

				return archivo

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
	
