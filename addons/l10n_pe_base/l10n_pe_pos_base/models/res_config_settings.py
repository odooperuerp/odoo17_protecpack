from odoo import models, api, fields, tools, _
from odoo.exceptions import UserError, ValidationError

import re
import logging
_logger = logging.getLogger(__name__)

pattern_number = "^[0-9]*$"

class PosConfig(models.Model):
    _inherit = "pos.config"

    pos_l10n_pe_invoice = fields.Boolean(string="Habilitar selección de tipo de documento")
    pos_l10n_pe_seq_factura = fields.Char(string="Factura", size=3)
    pos_l10n_pe_seq_boleta = fields.Char(string="Boleta", size=3)
    pos_l10n_pe_seq_nota_factura = fields.Char(string="Nota de crédito de factura", size=3)
    pos_l10n_pe_seq_nota_boleta = fields.Char(string="Nota de crédito de boleta", size=3)

    pos_l10n_pe_seqnum_factura = fields.Char(string="Número de factura", size=8, default=1)
    pos_l10n_pe_seqnum_boleta = fields.Char(string="Número de boleta", size=8, default=1)
    pos_l10n_pe_seqnum_nota_factura = fields.Char(string="Número de nota de factura", size=8, default=1)
    pos_l10n_pe_seqnum_nota_boleta = fields.Char(string="Número de nota de boleta", size=8, default=1)

    nv_journal_id = fields.Many2one(
        'account.journal', string='Diario de nota de venta',
        domain=[('type', 'in', ('general', 'sale'))],
        check_company=True,
        help="Diario para notas de venta desde el POS",
        ondelete='restrict')
    
    pos_l10n_pe_display_option = fields.Selection(
        [('logo', 'Imagen de Logo'), ('commercial_name', 'Nombre Comercial')],
        string="Opción de Visualización en Ticket",
        help="Indica si en el formato de ticket se visualizará la imagen del logo de la empresa o el nombre comercial.",
        default="commercial_name"
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_l10n_pe_invoice = fields.Boolean(related="pos_config_id.pos_l10n_pe_invoice", readonly=False)
    pos_l10n_pe_seq_factura = fields.Char(related="pos_config_id.pos_l10n_pe_seq_factura", readonly=False)
    pos_l10n_pe_seq_boleta = fields.Char(related="pos_config_id.pos_l10n_pe_seq_boleta", readonly=False)
    pos_l10n_pe_seq_nota_factura = fields.Char(related="pos_config_id.pos_l10n_pe_seq_nota_factura", readonly=False)
    pos_l10n_pe_seq_nota_boleta = fields.Char(related="pos_config_id.pos_l10n_pe_seq_nota_boleta", readonly=False)

    pos_l10n_pe_seqnum_factura = fields.Char(related="pos_config_id.pos_l10n_pe_seqnum_factura", readonly=False)
    pos_l10n_pe_seqnum_boleta = fields.Char(related="pos_config_id.pos_l10n_pe_seqnum_boleta", readonly=False)
    pos_l10n_pe_seqnum_nota_factura = fields.Char(related="pos_config_id.pos_l10n_pe_seqnum_nota_factura", readonly=False)
    pos_l10n_pe_seqnum_nota_boleta = fields.Char(related="pos_config_id.pos_l10n_pe_seqnum_nota_boleta", readonly=False)

    nv_journal_id = fields.Many2one("account.journal", related="pos_config_id.nv_journal_id", readonly=False)

    pos_l10n_pe_display_option = fields.Selection(related="pos_config_id.pos_l10n_pe_display_option", readonly=False)
    
    @api.onchange("pos_l10n_pe_seq_factura")
    def _onchange_upper_pos_l10n_pe_seq_factura(self):
        new_val = self.pos_l10n_pe_seq_factura
        if new_val:
            self.pos_l10n_pe_seq_factura = new_val.upper()
    
    @api.onchange("pos_l10n_pe_seq_boleta")
    def _onchange_upper_pos_l10n_pe_seq_boleta(self):
        new_val = self.pos_l10n_pe_seq_boleta
        if new_val:
            self.pos_l10n_pe_seq_boleta = new_val.upper()

    @api.onchange("pos_l10n_pe_seq_nota_factura")
    def _onchange_upper_pos_l10n_pe_seq_nota_factura(self):
        new_val = self.pos_l10n_pe_seq_nota_factura
        if new_val:
            self.pos_l10n_pe_seq_nota_factura = new_val.upper()

    @api.onchange("pos_l10n_pe_seq_nota_boleta")
    def _onchange_upper_pos_l10n_pe_seq_nota_boleta(self):
        new_val = self.pos_l10n_pe_seq_nota_boleta
        if new_val:
            self.pos_l10n_pe_seq_nota_boleta = new_val.upper()
    
    @api.onchange("pos_l10n_pe_seqnum_factura")
    def _onchange_pos_l10n_pe_seqnum_factura(self):
        new_val = self.pos_l10n_pe_seqnum_factura
        if new_val:
            if not re.match(pattern_number, new_val):
                _logger.info({'PATTERN MATCH': re.match(pattern_number, new_val)})
                self.pos_l10n_pe_seqnum_factura = ""
                raise ValidationError(_("El correlativo de inicio sólo puede ser numérico."))
            else:
                self.pos_l10n_pe_seqnum_factura = new_val
    
    @api.onchange("pos_l10n_pe_seqnum_boleta")
    def _onchange_pos_l10n_pe_seqnum_boleta(self):
        new_val = self.pos_l10n_pe_seqnum_boleta
        if new_val:
            if not re.match(pattern_number, new_val):
                _logger.info({'PATTERN MATCH': re.match(pattern_number, new_val)})
                self.pos_l10n_pe_seqnum_boleta = ""
                raise ValidationError(_("El correlativo de inicio sólo puede ser numérico."))
            else:
                self.pos_l10n_pe_seqnum_boleta = new_val

    @api.onchange("pos_l10n_pe_seqnum_nota_factura")
    def _onchange_pos_l10n_pe_seqnum_nota_factura(self):
        new_val = self.pos_l10n_pe_seqnum_nota_factura
        if new_val:
            if not re.match(pattern_number, new_val):
                _logger.info({'PATTERN MATCH': re.match(pattern_number, new_val)})
                self.pos_l10n_pe_seqnum_nota_factura = ""
                raise ValidationError(_("El correlativo de inicio sólo puede ser numérico."))
            else:
                self.pos_l10n_pe_seqnum_nota_factura = new_val
    
    @api.onchange("pos_l10n_pe_seqnum_nota_boleta")
    def _onchange_pos_l10n_pe_seqnum_nota_boleta(self):
        new_val = self.pos_l10n_pe_seqnum_nota_boleta
        if new_val:
            if not re.match(pattern_number, new_val):
                _logger.info({'PATTERN MATCH': re.match(pattern_number, new_val)})
                self.pos_l10n_pe_seqnum_nota_boleta = ""
                raise ValidationError(_("El correlativo de inicio sólo puede ser numérico."))
            else:
                self.pos_l10n_pe_seqnum_nota_boleta = new_val