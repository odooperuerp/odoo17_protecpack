from odoo.tests.common import TransactionCase, SingleTransactionCase
from odoo.tests import tagged
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from lxml import etree as ET
import logging
from odoo.tools.misc import file_path

_logger = logging.getLogger(__name__)


@tagged('external_l10n', 'post_install', '-at_install', 'external')
class TestValidationAccountMovePeru(SingleTransactionCase):

    def setUp(self):
        self.common()
        super(TestValidationAccountMovePeru, self).setUp()

    def common(self):
        partner = self.env["res.partner"]

        journal = self.env["account.journal"]

        #Diferentes tipos de empresas
        self.empresa = partner.create({
            "name": "ALICORP SAA",
            "l10n_latam_identification_type_id": self.env.ref("l10n_pe.it_RUC").id,
            "vat": "20100055237"
        })

        self.cliente_sin_empresa = partner.create({
            "name": "DANIEL MORENO",
            "l10n_latam_identification_type_id": self.env.ref("l10n_pe.it_DNI").id,
            "vat": "76310424"
        })

        #Diario
        self.diario = journal.create({
            "name": "Factura",
            "code": "FAC",
            "company_id": self.env.ref("base.main_company").id,
            "invoice_reference_type": "invoice",
            "type": "sale",
            "l10n_latam_use_documents": True,
            "invoice_reference_model": "odoo"
        })

        #Productos
        self.product_sin_impuestos = self.env['product.product'].create({
            'name': 'product_pe',
            'weight': 2,
            'uom_po_id': self.env.ref('uom.product_uom_kgm').id,
            'uom_id': self.env.ref('uom.product_uom_kgm').id,
            'lst_price': 1000.0,
        })

        self.product_con_impuestos = self.env['product.product'].create({
            'name': 'product_pe',
            'weight': 2,
            'uom_po_id': self.env.ref('uom.product_uom_kgm').id,
            'uom_id': self.env.ref('uom.product_uom_kgm').id,
            'lst_price': 1000.0,
        })

    #Restricción, Cuando la factura se publica, valida que el tipo y número de identidad del cliente sea correcto


    def test_factura_1(self):
        move = self.env["account.move"]
        self.factura = move.create({
            "partner_id": self.empresa.id,
            "currency_id": self.env.ref("base.PEN").id,
            "date": datetime.today(),
            "move_type": "out_invoice",
            "journal_id": self.diario.id,
            "l10n_latam_document_type_id": self.env.ref("l10n_pe.document_type01").id
        })
        self.factura.invoice_line_ids = [(0, 0, {
            'product_id': self.product_sin_impuestos.id,
            'product_uom_id': self.env.ref('uom.product_uom_kgm').id,
            'price_unit': 2000.0,
            'quantity': 5,
            'discount': 20.0
        })]
        #_logger.info(self.factura.read())
        self.factura.action_post()
        #self.factura.edi_document_ids._process_documents_web_services(with_commit=False)

        edi_str = self.factura.journal_id.edi_format_ids._generate_edi_invoice_bstr(self.factura)
        edi_str = edi_str.decode('latin1')
        edi_tree = ET.fromstring(edi_str)
        edi_tree = self.factura.company_id.l10n_pe_edi_certificate_id.sudo()._sign(edi_tree)
        #print(ET.tostring(edi_tree))

        with open(file_path('l10n_pe_edi_doc/tests/sunat_archivos/sfs/VALI/commons/xsl/validation/2.X/ValidaExprRegFactura-2.0.1.xsl'),'rb') as f_xsl:
            xsl_file = ET.parse(f_xsl)

        edi_filename = '%s-%s-%s' % (
            self.factura.company_id.vat,
            self.factura.l10n_latam_document_type_id.code,
            self.factura.name.replace(' ', ''),
        )
        todo_ok = True
        try:
            transform = ET.XSLT(xsl_file)
            result = transform(edi_tree,nombreArchivoEnviado=ET.XSLT.strparam(f'{edi_filename}.xml'))
        except Exception as e:
            _logger.info(f'log error {e}')
            todo_ok = False

        self.assertEqual(todo_ok, True)
        self.assertEqual(self.factura.state, "posted")

    def factura_2(self):
        move = self.env["account.move"]
        self.factura_2 = move.create({
            "partner_id": self.cliente_sin_empresa.id,
            "currency_id": self.env.ref("base.PEN").id,
            "date": datetime.today(),
            "move_type": "out_invoice",
            "journal_id": self.diario.id,
            "l10n_latam_document_type_id": self.env.ref("l10n_pe.document_type01").id
        })
        self.factura_2.invoice_line_ids = [(0, 0, {
            'product_id': self.product_sin_impuestos.id,
            'product_uom_id': self.env.ref('uom.product_uom_kgm').id,
            'price_unit': 2000.0,
            'quantity': 5,
            'discount': 20.0
        })]
        #_logger.info(self.factura.read())
        with self.assertRaises(ValidationError):
            self.factura_2.action_post()
