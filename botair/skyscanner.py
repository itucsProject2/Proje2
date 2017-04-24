from skyscanner.skyscanner import Flights
from skyscanner.skyscanner import FlightsCache
from django.http import HttpResponse
import requests, json, datetime


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
    
    query = ['bos'] * 4
    
    query[0] = place('ataturk')   # origin place
    query[1] = place('rome')  # destination place
    query[2] = '2017-05' # outbounddate
    query[3] = '2017-06'                 # inbounddate
    
    
    a = cheapestQuotes(query)
    if  a == None:
        return HttpResponse("ADAM GIBI ARAMA YAP SEKER COCUK")
    else:
        return HttpResponse(str(a))

def cheapestQuotes(query):
    
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
        originplace = originplace,
        destinationplace = destinationplace,
        outbounddate = outbounddate,
        inbounddate= inbounddate).parsed
    
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

def date(tarih):
    if tarih == '':
        return ''
    else:
        return str(tarih[6:] + '-' + tarih[3] + tarih[4] + '-' + tarih[:2])