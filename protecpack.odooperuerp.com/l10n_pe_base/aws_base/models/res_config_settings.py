from odoo import models,fields,api

class ResCompany(models.Model):
    _inherit = "res.company"

    #aws_iam_id = fields.Many2one("aws.iam",string = "AWS IAM")
    #aws_arn_ids = fields.Many2many("aws.arn","aws_iam_id",string = "ARNs")
    aws_iam_ids = fields.Many2many("aws.iam",string = "AWS IAM")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    #aws_iam_id = fields.Many2one("aws.iam",string = "AWS IAM",related="company_id.aws_iam_id",readonly=False)
    #aws_arn_ids = fields.Many2many("aws.arn","aws_iam_id",string = "ARNs",related="company_id.aws_arn_ids" ,readonly=False)
    aws_iam_ids = fields.Many2many("aws.iam",string = "AIMs",related="company_id.aws_iam_ids" ,readonly=False)
    group_use_aws = fields.Boolean(string="Accesos a servicios de AWS",implied_group="aws_base.group_aws_base_user")