from django.conf.urls import url, include
from .views import HomePageView

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='HomePage'),
    url('member', include('member_management.urls'))
]
