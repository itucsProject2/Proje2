from django.conf.urls import url, include
from .views import BotairView

urlpatterns = [
    url(r'^7a312b084fc7d66e792da1bc79a082d3f953142e3a947fa050/?$', BotairView.as_view())
    
]