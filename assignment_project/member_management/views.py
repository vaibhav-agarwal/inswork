# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from google.appengine.ext import db
from google.net.proto.ProtocolBuffer import ProtocolBufferEncodeError
import json
import logging
import traceback

from assignment import MemberException
from models import TeamMembers


class AddMemberView(View):


    def post(self, request):

        response_obj = {"success": False, "msg": ""}
        response = HttpResponse()
        response['Content-type'] = "application/json"

        member_json = request.body
        try:
            member_json = TeamMembers.sanitize_data(member_json)
            member_id = TeamMembers.add_member(member_json)
            if not member_id:
                raise MemberException("Sorry, Unable to add Member!")

            response.status_code = 201
            response_obj["success"] = True
            response_obj["member_id"] = member_id
            response_obj["uri"] = request.scheme + "://" + request.get_host() + "/inswork/member/%s" % member_id
            response_obj["msg"] = "Member has been added successfully!"

        except (ValueError, db.BadArgumentError, db.BadValueError) as e:
            response_obj["msg"] = "Bad Request >> " + str(e)
            response.status_code = 400
        except MemberException as e:
            response_obj["msg"] = "Conflict >> " + str(e.error)
            response.status_code = 409
        except:
            logging.error(traceback.format_exc())
            response_obj["msg"] = "Sorry, Your request could not be processed !"
            response.status_code = 500

        response.content = json.dumps(response_obj)
        return response


@method_decorator(csrf_exempt, name="dispatch")
class MemberView(View):

    def get(self, request, member_id):

        response_obj = {"success": False, "msg": ""}
        response = HttpResponse()
        response['Content-type'] = "application/json"

        try:
            member_id = int(member_id)
            obj = TeamMembers.get_member(member_id)
            response_obj["msg"] = "Member Details have been fetched successfully!"
            response_obj['member_details'] = obj
            response.status_code = 200
            response_obj["success"] = True

        except (ValueError, db.BadArgumentError, db.BadValueError, ProtocolBufferEncodeError) as e:
            response_obj["msg"] = "Bad Request >> " + str(e)
            response.status_code = 400
        except MemberException as e:
            response_obj["msg"] = "MemberNotFound >> " + str(e.error)
            response.status_code = 404
        except:
            logging.error(traceback.format_exc())
            response_obj["msg"] = "Sorry, Your request could not be processed !"
            response.status_code = 500

        response.content = json.dumps(response_obj)
        return response

    def put(self, request, member_id):

        response_obj = {"success": False, "msg": ""}
        response = HttpResponse()
        response['Content-type'] = "application/json"
        response['Access-Control-Allow-Origin'] = "*"

        member_json = request.body
        try:
            member_id = int(member_id)
            member_json = TeamMembers.sanitize_data(member_json)
            msg = TeamMembers.update_member(member_id, member_json)

            response.status_code = 200
            response_obj["success"] = True
            response_obj["member_id"] = member_id
            response_obj["uri"] = request.scheme + "://" + request.get_host() + "/inswork/member/%s" % member_id
            response_obj["msg"] = msg

        except (ValueError, db.BadArgumentError, db.BadValueError, ProtocolBufferEncodeError) as e:
            response_obj["msg"] = "Bad Request >> " + str(e)
            response.status_code = 400
        except MemberException as e:
            response_obj["msg"] = "MemberNotFound >> " + str(e.error)
            response.status_code = 404
        except:
            logging.error(traceback.format_exc())
            response_obj["msg"] = "Sorry, Your request could not be processed !"
            response.status_code = 500

        response.content = json.dumps(response_obj)
        return response

    def delete(self, request, member_id):

        response_obj = {"success": False, "msg": ""}
        response = HttpResponse()
        response['Content-type'] = "application/json"

        try:
            member_id = int(member_id)
            TeamMembers.delete_member(member_id)
            response_obj["msg"] = "Member has been deleted successfully!"
            response_obj['member_id'] = member_id
            response.status_code = 200
            response_obj["success"] = True

        except (ValueError, db.BadArgumentError, db.BadValueError, ProtocolBufferEncodeError) as e:
            response_obj["msg"] = "Bad Request >> " + str(e)
            response.status_code = 400
        except MemberException as e:
            response_obj["msg"] = "MemberNotFound >> " + str(e.error)
            response.status_code = 404
        except:
            logging.error(traceback.format_exc())
            response_obj["msg"] = "Sorry, Your request could not be processed !"
            response.status_code = 500

        response.content = json.dumps(response_obj)
        return response
