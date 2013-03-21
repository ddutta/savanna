from behave import *
from random import choice, randint
from string import ascii_lowercase
from sys import path
import RestApi
import json

path.append(path.append(".."))
rest = RestApi.RestApi()
global template_ids
template_ids = []

@When ('User see templates')
def get_templates(context):
    global status_code
    global res_content_list_templates
    res_content_list_templates = []
    res = rest.get_templates()
    status_code = res.status_code
    if status_code == 200:
         res_content_list_templates = json.loads(res.content)

@When ('User get template with id: "{n}"')
def get_template(context, n):
    global status_code
    global res_content_get_template
    res = rest.get_template(template_ids[int(n)])
    status_code = res.status_code
    if status_code == 200:
        res_content_get_template = json.loads(res.content)

@Given("node_template body")
def node_template_body(context):
    global template_body
    template_body = context.text

@When ('User create template')
def add_template(context):
    global template_body
    global status_code
    global res_content
    res = rest.create_template(template_body)
    status_code = res.status_code
    if status_code == 202:
        res_content = json.loads(res.content)
        template_ids.append(res_content['node_template'].get(u'id'))

@When ('User delete template with id: "{n}"')
def del_template(context, n):
    global status_code
    res = rest.delete_template(template_ids[int(n)])
    status_code = res.status_code

@When ('User put template with id: "{n}"')
def put_template(context, n):
    global status_code
    global res_content
    global template_body
    res = rest.create_template(template_body, template_ids[int(n)])
    status_code = res.status_code
    if status_code == 202:
        res_content = json.loads(res.content)

