from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View
from google.appengine.api import users

from assignment_utils import check_google_user_wrapper

class HomePageView(View):

    @check_google_user_wrapper
    def get(self, request):
        response = HttpResponse()
        response['Content-type'] = "text/html"

        html = "Welcome to InstaWork Assignment ! <br/>"
        html += "<a href='%s'>Logout</a>" % (users.create_logout_url(request.path))

        response.write(html)
        response.status_code = 200
        return response
