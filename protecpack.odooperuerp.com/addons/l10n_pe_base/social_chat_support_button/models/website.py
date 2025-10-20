from odoo import models,fields,api

class Website(models.Model):
    _inherit = "website"

    has_social_chat_support_button = fields.Boolean(string="Tiene Social Chat Support Button", default=False)
    social_chat_support_button_id = fields.Many2one("social.chat.support.button", string="Botón de soporte de chat social")



class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    has_social_chat_support_button = fields.Boolean(string="Tiene Social Chat Support Button", 
                                                        related="website_id.has_social_chat_support_button",
                                                        readonly=False)
    social_chat_support_button_id = fields.Many2one("social.chat.support.button", 
                                                        related="website_id.social_chat_support_button_id",
                                                        string="Botón de soporte de chat social", 
                                                        readonly=False)