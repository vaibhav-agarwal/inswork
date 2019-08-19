# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ValidationError
from google.appengine.ext import db
import json

from assignment import MemberException


class TeamMembersPhone(db.Model):

    """
    This Table stores phone as its key for faster retrieval and ensuring concurrent updates.
    Multiple members cannot have the same phone number at a time.
    """

    member_id = db.IntegerProperty()

    @classmethod
    def add_row(cls, phone, member_id):
        db_phone_row = cls(key_name=phone)
        db_phone_row.member_id = member_id
        return db_phone_row

    @classmethod
    def get_row(cls, phone_number, check_row=False):
        phone_row = cls.get_by_key_name(phone_number)
        if check_row and phone_row:
            raise MemberException("phone_exists", phone_row.member_id)

        return phone_row


class TeamMembersEmail(db.Model):

    """
    This Table stores email as its key for faster retrieval and ensuring concurrent updates.
    Multiple members cannot have the same email at a time.
    """

    member_id = db.IntegerProperty()

    @classmethod
    def add_row(cls, email, member_id):
        db_email_row = cls(key_name=email)
        db_email_row.member_id = member_id
        return db_email_row

    @classmethod
    def get_row(cls, email, check_row=False):
        email_row = cls.get_by_key_name(email)
        if check_row and email_row:
            raise MemberException("email_exists", email_row.member_id)

        return email_row


class TeamMembers(db.Model):

    """
    This is the primary table storing the member details.
    """

    ALLOWED_ROLES = ["regular", "admin"]

    first_name = db.StringProperty(indexed=False)
    last_name = db.StringProperty(indexed=False)
    phone_number = db.StringProperty()
    email = db.StringProperty()
    role = db.StringProperty(choices=ALLOWED_ROLES, indexed=False)
    created_at = db.DateTimeProperty(auto_now_add=True, indexed=False)
    modified_at = db.DateTimeProperty(auto_now=True, indexed=False)

    @staticmethod
    def sanitize_data(member_json):

        try:
            try:
                member_json = json.loads(member_json)

                first_name = member_json.get("first_name", None)
                last_name = member_json.get("last_name", None)
                phone_number = member_json.get("phone_number", None)
                email = member_json.get("email", None)
                role = member_json.get("role", None)
            except:
                raise ValidationError("Invalid JSON!")

            first_name_validator = forms.CharField(error_messages={"required": "First Name is required!"})
            last_name_validator = forms.CharField(error_messages={"required": "Last Name is required!"})
            phone_number_validator = forms.RegexField(regex=r'^\+[1-9]\d{1,14}$',
                                                      error_messages={"invalid": "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."})
            email_validator = forms.EmailField()
            role_validator = forms.ChoiceField(choices=[(allowed_role, None) for allowed_role in TeamMembers.ALLOWED_ROLES],
                                               error_messages={"invalid_choice": "Value of role should be either regular or admin"})

            first_name_validator.clean(first_name)
            last_name_validator.clean(last_name)
            phone_number_validator.clean(phone_number)
            email_validator.clean(email)
            role_validator.clean(role)

            return member_json

        except ValidationError as e:
            if isinstance(e[0][0], ValidationError):
                raise ValueError(e[0][0].message)
            else:
                raise ValueError(e[0])
        except:
            raise

    @classmethod
    def get_existing_member(cls, member_id):

        member_row = cls.get_by_id(member_id)
        if not member_row:
            raise MemberException("not_found", member_id)

        return member_row

    @classmethod
    def get_member(cls, member_id):

        member_row = cls.get_existing_member(member_id)

        obj = {}
        obj['member_id'] = member_row.key().id()
        obj['first_name'] = member_row.first_name
        obj['last_name'] = member_row.last_name
        obj['phone_number'] = member_row.phone_number
        obj['email'] = member_row.email
        obj['role'] = member_row.role

        return obj

    @classmethod
    @db.transactional(xg=True)
    def add_member(cls, member_json):                    # Transactional Block

        member_id = None

        phone_number = member_json.get("phone_number", None)
        email = member_json.get("email", None)

        phone_row = TeamMembersPhone.get_row(phone_number, check_row=True)
        email_row = TeamMembersEmail.get_row(email, check_row=True)

        db_row = cls()
        db_row.first_name = member_json.get("first_name", None)
        db_row.last_name = member_json.get("last_name", None)
        db_row.phone_number = member_json.get("phone_number", None)
        db_row.email = member_json.get("email", None)
        db_row.role = member_json.get("role", None)

        db_row.put()
        member_id = db_row.key().id()

        db_phone_row = TeamMembersPhone.add_row(phone_number, member_id)
        db_email_row = TeamMembersEmail.add_row(email, member_id)

        db.put([db_phone_row, db_email_row])              # Save multiple DB rows in single RPC Call.

        return member_id

    @classmethod
    @db.transactional(xg=True)
    def update_member(cls, member_id, member_json):      # Transactional Block

        phone_number = member_json.get("phone_number", None)
        email = member_json.get("email", None)
        first_name = member_json.get("first_name", None)
        last_name = member_json.get("last_name", None)
        role = member_json.get("role", None)

        member_row = cls.get_existing_member(member_id)
        are_details_updated = False
        rows_to_update = []
        rows_to_delete = []

        if phone_number != member_row.phone_number:
            old_phone_row = TeamMembersPhone.get_row(member_row.phone_number)
            new_phone_row = TeamMembersPhone.add_row(phone_number, member_id)
            rows_to_update.append(new_phone_row)
            rows_to_delete.append(old_phone_row)
            are_details_updated = True

        if email != member_row.email:
            old_email_row = TeamMembersEmail.get_row(member_row.email)
            new_email_row = TeamMembersEmail.add_row(email, member_id)
            rows_to_update.append(new_email_row)
            rows_to_delete.append(old_email_row)
            are_details_updated = True

        if (not are_details_updated) and ((first_name != member_row.first_name) or (last_name != member_row.last_name)
                                          or (role != member_row.role)):
            are_details_updated = True

        if are_details_updated:
            member_row.phone_number = phone_number
            member_row.email = email
            member_row.first_name = first_name
            member_row.last_name = last_name
            member_row.role = role

            rows_to_update.append(member_row)

            db.put(rows_to_update)                      # Save multiple DB rows in single RPC Call.
            db.delete(rows_to_delete)                   # Delete multiple DB rows in single RPC Call.

            msg = "Member has been updated successfully!"
        else:
            msg = "Member details are same...not updating record in DB"

        return msg

    @classmethod
    @db.transactional(xg=True)
    def delete_member(cls, member_id):                  # Transactional Block

        member_row = cls.get_existing_member(member_id)
        rows_to_delete = [member_row]
        phone_row = TeamMembersPhone.get_row(member_row.phone_number)
        if phone_row:
            rows_to_delete.append(phone_row)
        email_row = TeamMembersEmail.get_row(member_row.email)
        if email_row:
            rows_to_delete.append(email_row)

        db.delete(rows_to_delete)
