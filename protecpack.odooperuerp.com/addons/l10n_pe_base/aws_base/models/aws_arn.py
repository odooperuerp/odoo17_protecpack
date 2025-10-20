from odoo import models,fields,api
import re
import logging
_logger = logging.getLogger(__name__)


class AWSARN(models.Model):
    _name = "aws.arn"
    _description = "ARN"

    name = fields.Char(string = "Nombre",required=True)
    description = fields.Char(string = "Description")
    value = fields.Char(string = "Value",required=True)
    active = fields.Boolean(string = "Active", default = True)
    aws_iam_id = fields.Many2one("aws.iam",string = "IAM",required=True)
    region = fields.Selection(selection = [
                                    ('us-east-1', 'EEUU Este (Norte de Virginia)'),
                                    ('us-east-2', 'EEUU Este (Ohio)'),
                                    ('us-west-1', 'EEUU Oeste (Norte de California)'),
                                    ('us-west-2', 'EEUU Oeste (Oregón)'),
                                    ('af-south-1', 'África (Cabo)'),
                                    ('ap-east-1', 'Asia-Pacífico (Hong Kong)'),
                                    ('ap-south-1', 'Asia-Pacífico (Mumbai)'),
                                    ('ap-northeast-3', 'Asia-Pacífico (Osaka)'),
                                    ('ap-northeast-2', 'Asia-Pacífico (Seúl)'),
                                    ('ap-southeast-1', 'Asia-Pacífico (Singapur)'),
                                    ('ap-southeast-2', 'Asia-Pacífico (Sídney)'),
                                    ('ap-northeast-1', 'Asia-Pacífico (Tokio)'),
                                    ('ca-central-1', 'Canadá (Central)'),
                                    ('eu-central-1', 'Europa (Fráncfort)'),
                                    ('eu-west-1', 'Europa (Irlanda)'),
                                    ('eu-west-2', 'Europa (Londres)'),
                                    ('eu-south-1', 'Europa (Milán)'),
                                    ('eu-west-3', 'Europa (París)'),
                                    ('eu-north-1', 'Europa (Estocolmo)'),
                                    ('me-south-1', 'Oriente Medio (Bahrein)'),
                                    ('sa-east-1', 'Suramérica (São Paulo)')
                                ],string="Region",required=True)

    @api.onchange('value')
    def onchange_value(self):
        pattern = r":([a-z]{2}-[a-z]+-[0-9]+)"
        if self.value:
            res = re.search(pattern,self.value)
            if res:
                self.region = res.group(1)
            