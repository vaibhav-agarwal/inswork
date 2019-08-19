from django.http import HttpResponse
from google.appengine.api import users
import json


def check_google_user_wrapper(func):

    """
    Decorator for User Authentication.
    Reserved for Future Use.
    """

    def wrapper(self, *args, **kwargs):

        request = args[0]
        self.user = users.get_current_user()
        if self.user is None:
            response = HttpResponse()
            if request.method == "GET":
                response['Content-type'] = "text/html"
                response.write('Please login with your gmail id <a href="' + users.create_login_url(request.path) +
                               '"> Here</a>')
            else:
                login_url = request.scheme + "://" + request.get_host() + users.create_login_url(request.path)
                response['Content-type'] = "application/json"
                response.content = json.dumps({"success": False, "msg": "Please login with your gmail id",
                                               "login_url": login_url})
            response.status_code = 401
            return response

        return func(self, *args, **kwargs)

    return wrapper


class MemberException(Exception):

    def __init__(self, error_type, member_id):

        if error_type == "phone_exists":
            self.error = "Team Member with ID %s already exist with the given phone number." % member_id
        elif error_type == "email_exists":
            self.error = "Team Member with ID %s already exist with the given email." % member_id
        elif error_type == "not_found":
            self.error = "Team Member with ID %s does not exist !" % member_id
        elif error_type == "add_error":
            self.error = ""
