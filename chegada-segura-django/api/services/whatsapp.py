import requests
from django.conf import settings
class WhatsAppProvider:
    def send_template(self, *, to, template_name, language, body_parameters):
        if not settings.WHATSAPP_ENABLED:
            return {'provider_message_id':f'dev-{to}-{template_name}','provider_status':'sent'}
        if not settings.WHATSAPP_PHONE_NUMBER_ID or not settings.WHATSAPP_ACCESS_TOKEN:
            raise RuntimeError('WhatsApp está habilitado, mas PHONE_NUMBER_ID/ACCESS_TOKEN não foram configurados.')
        url=f'https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages'
        payload={'messaging_product':'whatsapp','to':to,'type':'template','template':{'name':template_name,'language':{'code':language},'components':[{'type':'body','parameters':[{'type':'text','text':str(x)} for x in body_parameters]}]}}
        r=requests.post(url,json=payload,headers={'Authorization':f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}'},timeout=15)
        if not r.ok: raise RuntimeError(f'WhatsApp HTTP {r.status_code}: {r.text[:500]}')
        data=r.json(); return {'provider_message_id':(data.get('messages') or [{}])[0].get('id'),'provider_status':'sent'}
whatsapp_provider=WhatsAppProvider()
