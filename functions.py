import copy
import json
import traceback

from bson import json_util, ObjectId

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

def convert_object_ids_to_string(data):
    if isinstance(data, dict):
        return {key: convert_object_ids_to_string(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_object_ids_to_string(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data
