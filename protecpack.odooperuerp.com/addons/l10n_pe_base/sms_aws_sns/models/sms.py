from odoo import api, fields, models, tools, _
import logging
from ..utils.service import SMS
from odoo.exceptions import UserError, ValidationError
import uuid

_logger = logging.getLogger(__name__)

class AWSSns:

    def __init__(self, env):
        self.env = env
        
    def _send_sms_batch(self, messages):
        aws_sns_arn_id = self.env.user.company_id.aws_sns_arn_id
        
        if not aws_sns_arn_id:
            raise UserError(_("No se ha configurado el ARN de AWS SNS"))

        aws_iam_id = aws_sns_arn_id.aws_iam_id

        ARN = aws_sns_arn_id.value
        ACCESS_KEY_ID = aws_iam_id.access_key_id
        SECRET_ACCESS_KEY = aws_iam_id.secret_access_key
        REGION = aws_sns_arn_id.region

        for message in messages:
            numbers = message.get("numbers")
            content = message.get("content")
            for number in numbers:
                sms = SMS(aws_access_key_id=ACCESS_KEY_ID, 
                            aws_secret_access_key=SECRET_ACCESS_KEY, 
                            region=REGION)
                subs = sms.subscribe(arn=ARN, phone=number.get("number"))
                if subs:
                    p = sms.publish(phone=number.get("number"), message=content)

                    if(p['ResponseMetadata']['HTTPStatusCode'] == 200):
                        _logger.info("El mensaje ha sido enviado")
                    else:
                        _logger.error("Mensaje no enviado")
                        return [{"uuid":uuid.uuid4(),'res_id':message.get("res_id"),'state':'server_error','credit':0} for message in messages]

                else: 
                    _logger.error("El número no pudo suscribirse")
                    return [{"uuid":uuid.uuid4(),'res_id':message.get("res_id"),'state':'server_error','credit':0} for message in messages]

        return [{"uuid":uuid.uuid4(),'res_id':message.get("res_id"),'state':'success','credit':0} for message in messages]



class SmsSms(models.Model):
    _inherit = "sms.sms"

    def _send(self, unlink_failed=False, unlink_sent=True, raise_exception=False):

        if not self.env.user.company_id.aws_sns_arn_id:
            return super(SmsSms, self)._send(unlink_failed=unlink_failed, unlink_sent=unlink_sent, raise_exception=raise_exception)

        messages = [{
            'content': body,
            'numbers': [{'number': sms.number, 'uuid': sms.uuid} for sms in body_sms_records],
        } for body, body_sms_records in self.grouped('body').items()]

        try:
            results = AWSSns(self.env)._send_sms_batch(messages) # Se cambio el Servicio AWSSns por SmsApi
        except Exception as e:
            _logger.info('Sent batch %s SMS: %s: failed with exception %s', len(self.ids), self.ids, e)
            if raise_exception:
                raise
            results = [{'uuid': sms.uuid, 'state': 'server_error'} for sms in self]
        else:
            _logger.info('Send batch %s SMS: %s: gave %s', len(self.ids), self.ids, results)

        results_uuids = [result['uuid'] for result in results]
        all_sms_sudo = self.env['sms.sms'].sudo().search([('uuid', 'in', results_uuids)]).with_context(sms_skip_msg_notification=True)

        for iap_state, results_group in tools.groupby(results, key=lambda result: result['state']):
            sms_sudo = all_sms_sudo.filtered(lambda s: s.uuid in {result['uuid'] for result in results_group})
            if success_state := self.IAP_TO_SMS_STATE_SUCCESS.get(iap_state):
                sms_sudo.sms_tracker_id._action_update_from_sms_state(success_state)
                to_delete = {'to_delete': True} if unlink_sent else {}
                sms_sudo.write({'state': success_state, 'failure_type': False, **to_delete})
            else:
                failure_type = self.IAP_TO_SMS_FAILURE_TYPE.get(iap_state, 'unknown')
                if failure_type != 'unknown':
                    sms_sudo.sms_tracker_id._action_update_from_sms_state('error', failure_type=failure_type)
                else:
                    sms_sudo.sms_tracker_id._action_update_from_provider_error(iap_state)
                to_delete = {'to_delete': True} if unlink_failed else {}
                sms_sudo.write({'state': 'error', 'failure_type': failure_type, **to_delete})

        all_sms_sudo.mail_message_id._notify_message_notification_update()



