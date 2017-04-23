from django.views import generic
from wit import Wit
from django.http.response import HttpResponse
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import requests
from pprint import pprint
from django.core.handlers.exception import response_for_exception


def post_facebook_message(fbid, message):           
        post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAPkuzQTj44BAD9sswQ97woRBzCuQf2FKvB757oF674ZB8xGfWqAKpNxveBexZCKWOlaaMtxJXVf7nilIHZAPYZAbdY5OeUPFwZCXYxU4GJRGHlmxijBq28oVcLmYovOm2gDZCGpDttRlPLf1Gxr4qyflAmHX9Gny0aN8wsKBzOQZDZD' 
        response_msg =json.dumps({"recipient":{"id":fbid}, "message":{"text":message}})
      
        status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
        pprint('In post_facebook_message function: ' + str(status.json()))


def first_entity_value(entities, entity):
    """
    Returns first entity value
    """
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val

def send(request, response):
    # We use the fb_id as equal to session_id
    fb_id = request['session_id']
    text = response['text']
    pprint('In send, text = ' + str(text))
    # send message
    post_facebook_message(fb_id, text)

def my_action(request):
    print('Received from user...', request['text'])


actions = {
    'send': send,
    'my_action':my_action,
    
}

# Setup Wit Client
client = Wit(access_token='DJE4HFOBMAJO6DMIC2IEZRP5DDRQRZKS', actions=actions)
#DJE4HFOBMAJO6DMIC2IEZRP5DDRQRZKS
#client.interactive()

def getEntityFromWit(textMessage):
    try:
        resp = client.message(textMessage)
        pprint('getEntityFromWit: get from wit:' + str(resp))
        return resp
    except:
        return('getEntityFromWit: send to wit.ai error')
        


class BotairView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == '150120017150120021150130281':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token') 
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)
    


    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            
            for message in entry['messaging']:
           
                if 'message' in message:
                    pprint('Message in post:' + str(message)) 
                    fb_id = message['sender']['id']
                    text = message['message']['text']
                    try:
                        #resp = sendToWit(str(text))
                        pprint('trying to client.run_actions text:' + str(text))
                        client.run_actions(fb_id,text)
                        #pprint('resp to wit : ' + str(resp))
                        
                        #post_facebook_message(fb_id, str(resp))
                        return HttpResponse()
                    except:
                        post_facebook_message(fb_id,'wit.ai error') 
                        return HttpResponse()
                    
                return HttpResponse()

#class BotairView(generic.View):
#    def get(self, request, *args, **kwargs):
#        if self.request.GET['hub.verify_token'] == '150120017150120021150130281':
#            return HttpResponse(self.request.GET['hub.challenge'])
#        else:
#            return HttpResponse('Error, invalid token')    
