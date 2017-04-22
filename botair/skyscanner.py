from skyscanner.skyscanner import Flights
from skyscanner.skyscanner import FlightsCache
from django.http import HttpResponse
import requests, json


def livePrices(request):
    
    flights_service = Flights('bo222919948041713910427845435861')
    
    result = flights_service.get_result(
        country='UK',
        currency='GBP',
        locale='en-GB',
        originplace='SIN-sky',
        destinationplace='KUL-sky',
        outbounddate='2017-05-28',
        inbounddate='2017-05-31',
        adults=1).parsed
    
    return HttpResponse(result)

def flightQuery(request):
    
    query = ['bos'] * 6
    query[0] = 'USD'
    query[1] = place('adana')   # origin place
    query[2] = place('hatay')  # destination place
    query[3] = '2017-05' # outbounddate
    query[4] = '' # inbounddate
    query[5] = 1        # kac tane sonuc istiyor
    if query[1] == '' or query[2] == '':
        return HttpResponse("ADAM GIBI ARAMA YAP LAN")
    
    if (len(query[3]) == len(query[3])) or (len(query[4]) == 0 and len(query[3]) > 0):  # TARIH KONTROL
        a = cheapestQuotes(query)
        if  a == None:
            return HttpResponse("ADAM GIBI ARAMA YAP LAN")
        else:
            return HttpResponse(a)
    else:
        return HttpResponse('Hatali Tarih')

def cheapestQuotes(query):
    
    data = json.loads(json.dumps({'price': 0, 'out': {'date': '', 'place':'', 'carrier':''}, 'in':{'date': '', 'place':' ', 'carrier':''}})) # direct???
    flights_cache_service = FlightsCache('bo222919948041713910427845435861')
    #return HttpResponse(query)
    result = flights_cache_service.get_cheapest_quotes(
    
        market = 'tr',
        currency = query[0],
        locale = 'en-US',
        originplace = query[1],
        destinationplace = query[2],
        outbounddate = query[3],
        inbounddate= query[4]).parsed
    
    if len(result['Quotes']) == 0:
        #return HttpResponse('ADAM GIBI ARAMA YAP LAN1')
        data = None
        return data
    
    if not 'InboundLeg' in result['Quotes'][0]:
        one_way = True
    else:
        one_way = False
        
    
    data['price'] = result['Quotes'][0]['MinPrice']
    
    data['out']['date'] = result['Quotes'][0]['OutboundLeg']['DepartureDate']
    if one_way != True:
        data['in']['date'] = result['Quotes'][0]['InboundLeg']['DepartureDate']
    
    for i in range(0, len(result['Places'])):   # DEPARTURE AIRPORTS
        if result['Places'][i]['Type'] == 'Airport' and result['Places'][i]['PlaceId'] == result['Quotes'][0]['OutboundLeg']['OriginId']:   #out
             data['out']['place'] = result['Places'][i]['Name']
             
        if one_way != True and result['Places'][i]['Type'] == 'Airport' and result['Places'][i]['PlaceId'] == result['Quotes'][0]['InboundLeg']['OriginId']:   #in
            data['in']['place'] = result['Places'][i]['Name']
            
    for i in range(0, len(result['Carriers'])):     # CARRIER NAMES
        if result['Carriers'][i]['CarrierId'] == result['Quotes'][0]['OutboundLeg']['CarrierIds'][0]:   #out
            data['out']['carrier'] = result['Carriers'][i]['Name']
            
        if one_way != True and result['Carriers'][i]['CarrierId'] == result['Quotes'][0]['InboundLeg']['CarrierIds'][0] and one_way != True:   #in
            data['in']['carrier'] = result['Carriers'][i]['Name']
    
    #para = result['Quotes'][0]['MinPrice']
    #para = result.json()
    return data

def currencies(birim):
    
    result = requests.get('http://partners.api.skyscanner.net/apiservices/reference/v1.0/currencies?apiKey=bo222919948041713910427845435861')
    currencies = result.json()
    k = 0
    for i in range(0,len(currencies['Currencies'])):
        if currencies['Currencies'][i]['Code'] == birim:
            deneme = currencies['Currencies'][i]['Symbol']
            #k = i
            #break
        k = i
    return HttpResponse(k)
    
def place(yer):

    result = requests.get('http://partners.api.skyscanner.net/apiservices/autosuggest/v1.0/tr/TRY/en-US?query=' + yer + '&apiKey=bo222919948041713910427845435861')
    place = result.json()
    if len(place['Places']) == 0:
        return ''
    
    CountryName = place['Places'][0]['CountryName']
    CityId = place['Places'][0]['CityId']
    PlaceName = place['Places'][0]['PlaceName']
    PlaceId = place['Places'][0]['PlaceId']     # havaalani id
    return str(PlaceId)
