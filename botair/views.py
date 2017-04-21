from django.views import generic
from django.http.response import HttpResponse
# Create your views here.

class BotairView(generic.View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Hello World!")