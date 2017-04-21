from django.views import generic
from django.http.response import HttpResponse
# Create your views here.

class BotairView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == 'EAAJPGyHraTUBAIiXMqZCZBtmZACxAmxQ9YZB9BZBCQao67vZADEfd2QMHiZBQDIHX621SFbEGRyIpdTxQIaiZBNskRiWg2r9mBap5jfjA6aOypHL4cHSe01vddzzEe8TFimUzGSF2WpCUWvlEgkItA5lFPan0iLozsMcH7pyokLaZCwZDZD':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
