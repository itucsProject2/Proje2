from skyscanner.skyscanner import Flights
from skyscanner.skyscanner import FlightsCache
from django.http import HttpResponse

def skyscanner(request):
    
    flights_cache_service = FlightsCache('bo222919948041713910427845435861')

    result = flights_cache_service.get_cheapest_quotes(
    
        market = 'TR',
        currency = 'TRY',
        locale = 'tr-TR',
        originplace = 'IST-sky',
        destinationplace = 'SIN-sky',
        outbounddate = '2017-05-28',
        inbounddate= '2017-05-31').parsed
    para = result['Quotes'][0]['MinPrice']
    #para = result.json()
    return HttpResponse(para)
    
###