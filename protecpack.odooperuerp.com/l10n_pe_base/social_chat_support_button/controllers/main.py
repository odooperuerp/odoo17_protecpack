from odoo import http,_,tools,SUPERUSER_ID
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale



class WebsiteSocialChat(WebsiteSale):

    @http.route(['/get_social_chat_button'], type='json', auth="public", website=True)
    def get_social_chat_button(self, website_id, **kw):
        result = {}
        if website_id:
            website = request.env['website'].sudo().browse(website_id)
            if website.has_social_chat_support_button:
                result = website.social_chat_support_button_id.get_as_json_for_czmChatSupport()

        return result
