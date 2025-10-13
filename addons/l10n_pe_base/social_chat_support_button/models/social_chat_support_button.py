from odoo import models,fields,api
import logging
import json
_logger = logging.getLogger(__name__)



COLORS_BACKGROUND = {
    "fa-whatsapp": "#10C379",
    "fa-messenger": "#0084FF",
    "fa-telegram": "#18A3E6"
}

class SocialChatSupportButtonAgent(models.Model):
    _name = "social.chat.support.button.agent"
    _description = "Social Chat Support Button Agent"

    social_avatar = fields.Selection(string = "Social Avatar", selection=[("fa-whatsapp", "Whatsapp"),
                                                                            ("fa-messenger","Messenger"),
                                                                            ("fa-telegram","Telegram"),
                                                                            ("ninguno","Ninguno")],required = True,default="fa-whatsapp")
    is_person = fields.Boolean("Es persona", default=False)
    avatar_image = fields.Binary("Imagen de avatar")
    avatar_src = fields.Char("src",compute="compute_avatar_src")

    @api.depends("is_person","avatar_image","social_avatar")
    def compute_avatar_src(self):
        for record in self:
            src = ""
            if record.is_person and record.avatar_image and isinstance(record._origin.id, int):
                src = "<img src='/web/image/social.chat.support.button.agent/%s/avatar_image' alt='Avatar'>" % record._origin.id
            elif record.social_avatar != "ninguno":
                src = "<i class='fa %s'></i>" % record.social_avatar
            record.avatar_src = src
    
    
    avatar_background_color = fields.Char("Color de fondo del avatar")

    @api.onchange("social_avatar")
    def onchange_avatar_background_color(self):
        self.avatar_background_color = COLORS_BACKGROUND.get(self.social_avatar,"#efefef")

    avatar_online_circle = fields.Boolean("Círculo en línea", default=True)

    text_title = fields.Char("Título",required=True)
    text_description = fields.Char("Descripción")
    text_online = fields.Char("Texto en línea")
    text_offline = fields.Char("Texto fuera de línea")

    text_message = fields.Char("Mensaje de texto", default="Hola, ¿en qué puedo ayudarte?")
    text_textbox = fields.Char("Texto del cuadro de texto", default="Escribe tu mensaje aquí")
    text_button = fields.Boolean("Botón de texto", default=False)


    link_desktop = fields.Char("Enlace escritorio",default="https://web.whatsapp.com/send?phone=5199999999&text=Hi")
    link_mobile = fields.Char("Enlace móvil",default="https://wa.me/5199999999/?text=Hi")

    online_day_sunday_start = fields.Float("Inicio del domingo en línea")
    online_day_sunday_end = fields.Float("Fin del domingo en línea")

    online_day_monday_start = fields.Float("Inicio del lunes en línea")
    online_day_monday_end = fields.Float("Fin del lunes en línea")

    online_day_tuesday_start = fields.Float("Inicio del martes en línea")
    online_day_tuesday_end = fields.Float("Fin del martes en línea")

    online_day_wednesday_start = fields.Float("Inicio del miércoles en línea")
    online_day_wednesday_end = fields.Float("Fin del miércoles en línea")

    online_day_thursday_start = fields.Float("Inicio del jueves en línea")
    online_day_thursday_end = fields.Float("Fin del jueves en línea")

    online_day_friday_start = fields.Float("Inicio del viernes en línea")
    online_day_friday_end = fields.Float("Fin del viernes en línea")

    online_day_saturday_start = fields.Float("Inicio del sábado en línea")
    online_day_saturday_end = fields.Float("Fin del sábado en línea")

    social_chat_support_button_id = fields.Many2one("social.chat.support.button", "Botón de soporte de chat social")

    @api.model
    def get_schedule_text(self,start,end):
        if start and end:
            start_hour = int(start)
            start_minute = int((start - start_hour) * 60)
            end_hour = int(end)
            end_minute = int((end - end_hour) * 60)
            return "%s:%s-%s:%s" % (start_hour,start_minute,end_hour,end_minute)
        return ""



class SocialChatSupportButton(models.Model):
    _name = "social.chat.support.button"
    _description = "Social Chat Support Button"

    name = fields.Char("Nombre", default="Botón de soporte de chat social")
    style = fields.Selection(selection=[("1", "Estilo 1"),
                                        ("2", "Estilo 2"),
                                        ("3", "Estilo 3"),
                                        ("4", "Estilo 4"),
                                        ("5", "Estilo 5"),
                                        ("6", "Estilo 6"),
                                        ("7", "Estilo 7")], string="Estilo",required=True,default="1")

    position = fields.Selection(string = "Posición", selection=[("left", "Left"),("right", "Right")],required=True,default="right")    
    
    
    avatar_type = fields.Selection(string = "Tipo de avatar", selection=[("image", "Imagen"),("icon", "Icono")],required=True,default="icon")

    social_avatar_icon = fields.Selection(string = "Social Avatar Icon", selection=[("fa-whatsapp", "Whatsapp"),
                                                                        ("fa-messenger","Messenger"),
                                                                        ("fa-telegram","Telegram"),
                                                                        ("ninguno","Ninguno")])
    social_avatar_image = fields.Binary("Social Avatar Image")

    src = fields.Char("Imagen de avatar",compute="compute_avatar_type")

    text_title = fields.Char("Título",required=True)
    text_description = fields.Char("Descripción")
    text_online = fields.Char("Texto en línea")
    text_offline = fields.Char("Texto fuera de línea")
    
    link_desktop = fields.Char("Enlace escritorio",default="https://web.whatsapp.com/send?phone=5199999999&text=Hi")
    link_mobile = fields.Char("Enlace móvil",default="https://wa.me/5199999999/?text=Hi")

    background_color = fields.Char("Color de fondo", default="#efefef")

    @api.depends("avatar_type","social_avatar_icon","social_avatar_image")
    def compute_avatar_type(self):
        for record in self:
            src = ""
            if record.avatar_type == "icon" and record.social_avatar_icon:
                src = "<i class='fa %s'></i>" % record.social_avatar_icon
            elif record.avatar_type == "image" and record.social_avatar_image and isinstance(record._origin.id, int):
                src = "<img src='/web/image/social.chat.support.button/%s/social_avatar_image' alt='Avatar'>" % record._origin.id

            record.src = src

    effect = fields.Selection(string = "Efecto", selection=[("1", "Efecto 1"),
                                                    ("2", "Efecto 2"),
                                                    ("3", "Efecto 3"),
                                                    ("4", "Efecto 4"),
                                                    ("5", "Efecto 5"),
                                                    ("6", "Efecto 6"),
                                                    ("7", "Efecto 7")])

    pulse_effect = fields.Boolean("Efecto de pulso", default=False)

    speech_bubble = fields.Char("Burbuja de discurso", default="¿En qué puedo ayudarte?")

    notification_number = fields.Boolean("Notificación", default= False)
    
    display_frequency = fields.Integer("Frecuencia de visualización (h)", default=1)

    popup_automatic_open = fields.Boolean("Apertura automática de popup?", default=False)
    popup_outside_click_close_popup = fields.Boolean("Cerrar popup al hacer clic fuera?", default=False)
    popup_effect = fields.Selection(string = "Efecto de popup", selection=[("1", "Efecto Popup 1"),
                                                                                ("2", "Efecto Popup 2"),
                                                                                ("3", "Efecto Popup 3"),
                                                                                ("4", "Efecto Popup 4"),
                                                                                ("5", "Efecto Popup 5"),
                                                                                ("6", "Efecto Popup 6"),
                                                                                ("7", "Efecto Popup 7"),
                                                                                ("8", "Efecto Popup 8"),
                                                                                ("9", "Efecto Popup 9"),
                                                                                ("10", "Efecto Popup 10"),
                                                                                ("11", "Efecto Popup 11"),
                                                                                ("12", "Efecto Popup 12"),
                                                                                ("13", "Efecto Popup 13"),
                                                                                ("14", "Efecto Popup 14")])
    popup_header_background_color = fields.Char("Color de fondo del encabezado del popup", default="#25d366")

    @api.onchange("social_avatar_icon","avatar_type")
    def onchange_social_avatar_icon(self):
        self.popup_header_background_color = COLORS_BACKGROUND.get(self.social_avatar_icon,"#efefef")
        self.background_color = COLORS_BACKGROUND.get(self.social_avatar_icon,"#efefef")
    

    popup_header_title = fields.Char("Título del encabezado de la ventana emergente", default="¿Necesitas ayuda? Escríbenos")
    popup_header_description = fields.Char("Descripción del encabezado de la ventana emergente", default="¡Hola! ¿En qué puedo ayudarte?")

    sound = fields.Boolean("Sonido", default=False)
    cookie = fields.Integer("Cookie", default=0, help = "No vuelve a mostrar el popup, el número de notificación, el efecto de pulso y la ventana emergente de apertura automática durante el tiempo especificado. Por ejemplo, no mostrar durante 1 hora")

    social_chat_support_button_agent_ids = fields.One2many("social.chat.support.button.agent", "social_chat_support_button_id", "Agentes de soporte de chat social")

    json_for_csmChatSupport = fields.Json("JSON para csmChatSupport",compute="compute_json")

    @api.depends("name","avatar_type","social_avatar_icon","social_avatar_image","text_title","text_description","text_online","text_offline","link_desktop","link_mobile","background_color","effect","pulse_effect","speech_bubble","notification_number","popup_automatic_open","popup_outside_click_close_popup","popup_effect","popup_header_background_color","popup_header_title","popup_header_description","sound","cookie","social_chat_support_button_agent_ids")
    def compute_json(self):
        for record in self:
            record.json_for_csmChatSupport = self.get_as_json_for_czmChatSupport()

    def get_as_json_for_czmChatSupport(self): 
        result = {}
        button = {}
        link = {}
        text = {}
        popup = {}
        header = {}
        persons = []

        agent = self.env["social.chat.support.button.agent"]
        
        text.update(title = self.text_title or "",
                    description = self.text_description or False,
                    online = self.text_online or False,
                    offline = self.text_offline or False)
        
        link.update(
            desktop = self.link_desktop or False,
            mobile = self.link_mobile or False
        )

        button.update(position = self.position,
                        style = int(self.style),
                        backgroundColor = self.background_color,
                        src = self.src or "",
                        effect = int(self.effect),
                        pulseEffect = self.pulse_effect,
                        speechBubble = self.speech_bubble,
                        text = text or "")
                        
        if self.notification_number:
            button.update(notificationNumber = "1")

        if self.link_desktop or self.link_mobile:
            button.update(link = link)

        header.update(backgroundColor = self.popup_header_background_color,
                        title = self.popup_header_title,
                        description = self.popup_header_description)

        for agent in self.social_chat_support_button_agent_ids:
            person = {
                "avatar": {
                    "src": agent.avatar_src or "",
                    "backgroundColor": agent.avatar_background_color,
                    "onlineCircle": agent.avatar_online_circle
                },
                "text": {
                    "title": agent.text_title or "",
                    "description": agent.text_description or False,
                    "online": agent.text_online or False,
                    "offline": agent.text_offline or False,
                    "message": agent.text_message or "",
                    "textbox": agent.text_textbox or "",
                    "button": agent.text_button
                },
                "link": {
                    "desktop": agent.link_desktop or False,
                    "mobile": agent.link_mobile or False
                },
                "onlineDay": {
                    "sunday": agent.get_schedule_text(agent.online_day_sunday_start,agent.online_day_sunday_end),
                    "monday": agent.get_schedule_text(agent.online_day_monday_start,agent.online_day_monday_end),
                    "tuesday": agent.get_schedule_text(agent.online_day_tuesday_start,agent.online_day_tuesday_end),
                    "wednesday": agent.get_schedule_text(agent.online_day_wednesday_start,agent.online_day_wednesday_end),
                    "thursday": agent.get_schedule_text(agent.online_day_thursday_start,agent.online_day_thursday_end),
                    "friday": agent.get_schedule_text(agent.online_day_friday_start,agent.online_day_friday_end),
                    "saturday": agent.get_schedule_text(agent.online_day_saturday_start,agent.online_day_saturday_end)
                }
            }

            persons.append(person)

        popup.update(automaticOpen = self.popup_automatic_open,
                    outsideClickClosePopup = self.popup_outside_click_close_popup,
                    effect = self.popup_effect,
                    header = header,
                    persons = persons)

        result.update(sound = self.sound,
                    changeBrowserTitle = "Nuevo Mensaje!", 
                    cookie = False if self.cookie == 0 else self.cookie,
                    button = button,
                    popup = popup)

        return result