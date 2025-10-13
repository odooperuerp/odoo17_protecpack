from odoo import models, fields, api

class AWSIAM(models.Model):
    _name = "aws.iam"
    _description = "IAM User"
    
    name = fields.Char("Name",required=True)
    description = fields.Text("Description")
    access_key_id = fields.Char("Access Key ID",required=True)
    secret_access_key = fields.Char("Secret Access Key",required=True)
    active = fields.Boolean("Active", default=True)
    aws_arn_ids = fields.One2many("aws.arn", "aws_iam_id", "ARNs")