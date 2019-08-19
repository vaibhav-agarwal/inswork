from django.conf.urls import url

from .views import AddMemberView, MemberView

urlpatterns = [
    url(r'^/add$', AddMemberView.as_view(), name='AddMember'),
    url(r'^/(?P<member_id>[0-9]+\d)$', MemberView.as_view(), name='Member')
]
