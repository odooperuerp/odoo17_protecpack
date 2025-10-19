import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError
import logging
_logger=logging.getLogger(__name__)

class PleFixedAsset(models.Model):
	_name='ple.fixed.asset'
	_inherit='ple.base'
	_description = "Modulo PLE Libros Activos Fijos"
	_rec_name='periodo_ple'


	ple_fixed_asset_line_ids=fields.One2many('ple.fixed.asset.line','ple_fixed_asset_id',
		string="Libro Activos Fijos 7.1",readonly=True)

	periodo_ple=fields.Char(string="Periodo",compute="compute_campo_periodo",store=True)

	conjunto_activos_fijos=[]

	date_to=fields.Date(string="Hasta la Fecha:")

	###############################################################3

	@api.depends('fiscal_year','fiscal_month')
	def compute_campo_periodo(self):
		for ple in self:
			if ple.fiscal_year and ple.fiscal_month:
				ple.periodo_ple = "%s-%s-00" % (ple.fiscal_year or 'YYYY', ple.fiscal_month or 'MM') 
			else:
				ple.periodo_ple = 'Nuevo Registro'



	def open_wizard_print_form(self):
		res = super(PleFixedAsset,self).open_wizard_print_form()

		view = self.env.ref('ple_fixed_asset.view_wizard_printer_ple_fixed_asset_form')
		if view:

			return {
				'name': _('FORMULARIO DE IMPRESIÓN DEL LIBRO PLE'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'wizard.printer.ple.fixed.asset',
				'views': [(view.id,'form')],
				'view_id': view.id,
				'target': 'new',
				'context': {
					'default_ple_fixed_asset_id': self.id,
					'default_company_id' : self.company_id.id,}}



	def name_get(self):
		result = []
		for ple in self:

			if ple.date_to:
				result.append((ple.id, ple.date_to.strftime("%Y-%m-%d") or 'New'))
			else:
				result.append((ple.id,'New'))
		return result


	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []

		if self.date_to:
			recs = self.search([('date_to', operator, name)] + args, limit=limit)
		return recs.name_get()


	def _get_datas(self, domain):
		orden=""
		return self._get_query_datas('account.asset', domain, orden)



	def _get_domain(self):
		domain = [
			('state','not in',['draft','model']),
			('is_intangible','!=',True)
			]

		if self.date_to:
			domain.append(('acquisition_date','<=',self.date_to.strftime("%Y-%m-%d")))
		
		return domain



	def _periodo_fiscal(self):
		if self.date_to:
			month = '{:02}'.format(int(self.date_to.month))
			year = str(self.date_to.year)

			periodo = "%s%s00" % (year,month)
			return periodo
		else:
			return "YYYYMMDD"



	def generar_libro(self):
		self.state='open'
		self.ple_fixed_asset_line_ids.unlink()
		registro=[]
		
		#depreciation_move_ids : lineas de depreciación
		#original_move_line_ids : Lineas de facturas

		for line in self._get_datas(self._get_domain()):

			original_move_line_id = line.original_move_line_ids and line.original_move_line_ids[0]
			move_id = False

			if original_move_line_id:
				move_id = original_move_line_id
			
			registro.append((0,0,{
				'move_id':move_id and move_id.id or False,
				'account_id': line.account_asset_id and line.account_asset_id.id or False,
				'account_asset_id':line.id ,
				'periodo':self._periodo_fiscal()}))
			
		self.ple_fixed_asset_line_ids = registro