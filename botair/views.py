from django.views import generic
from wit import Wit
from skyscanner.skyscanner import FlightsCache
#from botair import skyscanner
from django.http.response import HttpResponse
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import requests, datetime
from pprint import pprint
from django.core.handlers.exception import response_for_exception

flyFlag = False
infoArray = [None] * 4


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
    t = str(text)
    t = t[:-1]
    t = t[2:]
    # send message
    
    post_facebook_message(fb_id, str(t))

def my_action(request):
    print('Received from user...', request['text'])

actions = {
    'send': send,
    'my_action':my_action,
}
 


#DJE4HFOBMAJO6DMIC2IEZRP5DDRQRZKS
#client.interactive()
client = Wit(access_token='DJE4HFOBMAJO6DMIC2IEZRP5DDRQRZKS', actions=actions)
def getEntityFromWit(textMessage):
    try:
        result = []
        resp = client.message(textMessage)
        pprint('resp in getEntitiy:' + str(resp))
        if 'location' in resp['entities']:
            pprint('KONTROL1')
            for location in resp['entities']['location']:
                result.append(str(location['value']))
        if 'datetime' in resp['entities']:  
            pprint('KONTROL2')
            for datetime in resp['entities']['datetime']:
                result.append(str(datetime['value']))
        if len(result) != 0:
                pprint('result in get Entity: ' + str(result))
                if len(result) == 1:
                    return 'I couldnt find your destination in your message. Please enter your message like: "I want to go from '+result[0] +' to destination"'
                returnMessage = cheapestQuotes(result)
                #return 'Listing flights from '+result[0]+' to '+result[1]
                pprint('SKYSCANNER = ' + str(returnMessage))
                if returnMessage['in']['origin'] == '':
                    return 'From: ' + returnMessage['out']['origin'] +'\nTo: ' + returnMessage['out']['destination'] +'\nDate: ' + returnMessage['out']['date']  + '\nCarrier: ' + returnMessage['out']['carrier']+ '\nPrice: ' + str(returnMessage['price'])
                else:
                    return 'OUTGOING:\nFrom: '+ returnMessage['out']['origin'] +'\nTo: ' + returnMessage['out']['destination'] +'\nDate: ' + returnMessage['out']['date']  + '\nCarrier: ' + returnMessage['out']['carrier']+ '\nPrice: ' + str(returnMessage['price']) + '\nRETURN:\nFrom: ' + returnMessage['out']['origin'] +'\nTo: ' + returnMessage['out']['destination'] +'\nDate: ' + returnMessage['out']['date']  + '\nCarrier: ' + returnMessage['out']['carrier']+ '\nPrice: '

        return ' '
    except Exception as e:
        return('getEntityFromWit: send to wit.ai error: ' + str(e))
        


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
                        result = getEntityFromWit(text)
                        if result == ' ' and text.find("error") == -1 and text.find("See") == -1 :
                            client.run_actions(fb_id,text)
                        else:
                            post_facebook_message(fb_id, str(result))
                        #pprint('resp to wit : ' + str(resp))
                        
                        #post_facebook_message(fb_id, str(resp))
                        return HttpResponse()
                    except Exception as e:
                        post_facebook_message(fb_id,'wit.ai error:' + str(e)) 
                        return HttpResponse()
                    
                return HttpResponse()

def cheapestQuotes(query):
    pprint('CHEAPEST')
    if len(query) == 2:
        outbounddate = str(datetime.date.today())
        inbounddate = ''
    elif len(query) == 3:
        outbounddate = query[2]
        inbounddate = ''
    else:
        outbounddate = query[2]
        inbounddate = query[3]
        
        if len(outbounddate) != len(inbounddate):
            return 'Tarihler Eslesmiyor'
        
    originplace = query[0]
    destinationplace = query[1]

        
    if inbounddate == '':
        one_way = True
    else:
        one_way = False
        
    data = json.loads(json.dumps({'price': 0, 'direct': True, 'out': {'date': '', 'origin':'', 'destination': '', 'carrier':''}, 'in':{'date': '', 'origin':'', 'destination': '', 'carrier':''}})) # direct???
    flights_cache_service = FlightsCache('bo222919948041713910427845435861')
    #return HttpResponse(query)
    result = flights_cache_service.get_cheapest_quotes(
    
        market = 'tr',
        currency = 'USD',
        locale = 'en-US',
        originplace = place(originplace),
        destinationplace = place(destinationplace),
        outbounddate = outbounddate[:10],
        inbounddate= inbounddate[:10]).parsed
    
    if len(result['Quotes']) == 0:  # parametrelere uyan sonuc yok
        #return HttpResponse('ADAM GIBI ARAMA YAP LAN1')
        return 'Parametrelere Uyan Sonuc Yok'
    
    queryIndex = 0  # gecerli query index
    
    for i in range(0,len(result['Quotes'])):
        
        if one_way and not 'InboundLeg' in result['Quotes'][i]:
            queryIndex = i
            break
        elif not one_way and 'InboundLeg' in result['Quotes'][i]:
            queryIndex = i
            break
        
    data['direct'] = result['Quotes'][queryIndex]['Direct']
    data['price'] = result['Quotes'][queryIndex]['MinPrice']
    
    temp = result['Quotes'][queryIndex]['OutboundLeg']['DepartureDate']
    data['out']['date'] = temp[:10]
    
    if one_way != True:
        temp = result['Quotes'][queryIndex]['InboundLeg']['DepartureDate']
        data['in']['date'] = temp[:10]
        
    for i in range(0, len(result['Places'])):   # DEPARTURE AIRPORTS
        if result['Places'][i]['Type'] == 'Station' and result['Places'][i]['PlaceId'] == result['Quotes'][queryIndex]['OutboundLeg']['OriginId']:   #out
            data['out']['origin'] = result['Places'][i]['Name']
        if result['Places'][i]['Type'] == 'Station' and result['Places'][i]['PlaceId'] == result['Quotes'][queryIndex]['OutboundLeg']['DestinationId']:   #out
            data['out']['destination'] =result['Places'][i]['Name']
        
        if one_way != True and result['Places'][i]['Type'] == 'Station' and result['Places'][i]['PlaceId'] == result['Quotes'][queryIndex]['InboundLeg']['OriginId']:   #in
            data['in']['origin'] = result['Places'][i]['Name']
            
        if one_way != True and result['Places'][i]['Type'] == 'Station' and result['Places'][i]['PlaceId'] == result['Quotes'][queryIndex]['InboundLeg']['DestinationId']:   #in
            data['in']['destination'] = result['Places'][i]['Name']
            
    for i in range(0, len(result['Carriers'])):     # CARRIER NAMES
        if result['Carriers'][i]['CarrierId'] == result['Quotes'][queryIndex]['OutboundLeg']['CarrierIds'][0]:   #out
            data['out']['carrier'] = result['Carriers'][i]['Name']
            
        if one_way != True and result['Carriers'][i]['CarrierId'] == result['Quotes'][queryIndex]['InboundLeg']['CarrierIds'][0] and one_way != True:   #in
            data['in']['carrier'] = result['Carriers'][i]['Name']
    
    #para = result['Quotes'][0]['MinPrice']
    #para = result.json()
    return data

def place(yer):
    if yer == '':
        return ''
    result = requests.get('http://partners.api.skyscanner.net/apiservices/autosuggest/v1.0/tr/TRY/en-US?query=' + yer + '&apiKey=bo222919948041713910427845435861')
    place = result.json()
    if len(place['Places']) == 0:
        return ''
    
    CountryName = place['Places'][0]['CountryName']
    CityId = place['Places'][0]['CityId']
    PlaceName = place['Places'][0]['PlaceName']
    PlaceId = place['Places'][0]['PlaceId']     # havaalani id
    return str(PlaceId)
#class BotairView(generic.View):
#    def get(self, request, *args, **kwargs):
#        if self.request.GET['hub.verify_token'] == '150120017150120021150130281':
#            return HttpResponse(self.request.GET['hub.challenge'])
#        else:
#            return HttpResponse('Error, invalid token')    
