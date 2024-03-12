import copy
import json
import traceback
from mongoengine.queryset.queryset import QuerySet
from bson import DBRef, json_util, ObjectId

from htmlcodes import *


def return_oid(_id):
    return _id if type(_id) is ObjectId else ObjectId(_id)


def print_and_return_error(e):
    traceback.print_exception(type(e), e, e.__traceback__)
    return edit_html_desc(ERROR_400, str(e))


def append_data(data, html_response):
    to_bytes = json_util.dumps(data)
    response = copy.deepcopy(html_response)
    response[0]['data'] = to_bytes
    return response


def append_data2(data, html_response):
    to_bytes = json.loads(json_util.dumps(data,default=str))
    response = copy.deepcopy(html_response)
    response[0]['data'] = to_bytes
    print('aa')
    print(response)
    return response

def edit_html_desc(html_response, new_desc):
    new_response = copy.deepcopy(html_response)
    new_response[0]['Description'] = new_desc
    return new_response

def convert_object_ids_to_string(obj):
    if isinstance(obj, dict):
        # Convert each value in the dictionary
        for key, value in obj.items():
            obj[key] = convert_object_ids_to_string(value)
    elif isinstance(obj, list):
        # Convert each element in the list
        for i in range(len(obj)):
            obj[i] = convert_object_ids_to_string(obj[i])
    elif isinstance(obj, ObjectId):
        # Convert ObjectId to string
        return str(obj)
    elif isinstance(obj, QuerySet):
        # Convert QuerySet to a list of dictionaries
        return convert_object_ids_to_string(list(obj))
    elif isinstance(obj, DBRef):
        # Handle DBRef objects (customize as needed)
        return str(obj.id)
    # Add more custom logic for other non-serializable types if needed

    return obj