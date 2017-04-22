from django.views import generic
from botair import witOperations
from django.http.response import HttpResponse
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import requests
from pprint import pprint

# Create your views here.

def post_facebook_message(fbid, recevied_message):           
        post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAPkuzQTj44BAD9sswQ97woRBzCuQf2FKvB757oF674ZB8xGfWqAKpNxveBexZCKWOlaaMtxJXVf7nilIHZAPYZAbdY5OeUPFwZCXYxU4GJRGHlmxijBq28oVcLmYovOm2gDZCGpDttRlPLf1Gxr4qyflAmHX9Gny0aN8wsKBzOQZDZD' 
        response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":recevied_message}})
        status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
        pprint(status.json())


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
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message:
                    # Print the message to the terminal
                    pprint(message)
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly.
                   # locationString = []
                    resp = witOperations.sendToWit(message['message']['text']) 
                    if resp is None:
                        resp = 'nothing in here'
                    pprint('Yay, got Wit.ai response: ' + str(resp))
                    post_facebook_message(message['sender']['id'],str(resp))      
        return HttpResponse()
    

#class BotairView(generic.View):
#    def get(self, request, *args, **kwargs):
#        if self.request.GET['hub.verify_token'] == '150120017150120021150130281':
#            return HttpResponse(self.request.GET['hub.challenge'])
#        else:
#            return HttpResponse('Error, invalid token')    
