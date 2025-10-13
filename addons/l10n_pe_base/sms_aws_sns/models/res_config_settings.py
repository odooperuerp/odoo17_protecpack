
from odoo import models,fields,api
import logging  

class ResCompany(models.Model):
    _inherit = "res.company"

    aws_sns_arn_id = fields.Many2one("aws.arn",string="ARN AWS SNS")

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    aws_sns_arn_id = fields.Many2one("aws.arn",string="ARN AWS SNS",related="company_id.aws_sns_arn_id",readonly=False)
