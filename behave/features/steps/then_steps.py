from behave import *
from re import match, search

@Then('Response is "{res_code}"')
def chkStatus(context, res_code):
    global status_code
    print("%s == %s" % (status_code, res_code))
    assert status_code == int(res_code.strip())

@Then('Response list of list clusters:"{list}"')
def response_list_clusters(context, list):
    global res_content_list_clusters
    names = []
    loop = res_content_list_clusters['clusters']
    for x in loop:
        names.append(x.pop(u'name'))
    print("%s == %s" % (names, list))
    assert str(names) == str(list)

@Then('Response for list cluster by id is:"{list}"')
def response_get_cluster(context, list):
    global res_content_get_cluster
    cluster = res_content_get_cluster['cluster']
    id = cluster.pop(u'id')
    print("%s == %s" % (cluster, list))
    assert str(cluster) == str(list)

@Then('Response list of list node_templates:"{list}"')
def response_list_node_templates(context, list):
    global res_content_list_templates
    names = []
    loop = res_content_list_templates['node_templates']
    for x in loop:
        names.append(x.pop(u'name'))
    print("%s == %s" % (names, list))
    assert str(names) == str(list)

@Then('Response for list node_template by id is:"{list}"')
def response_get_cluster(context, list):
    global res_content_get_template
    template = res_content_get_template['node_template']
    id = template.pop(u'id')
    print("%s == %s" % (template, list))
    assert str(template) == str(list)

@Then('Error content:"{list}"')
def error_content(content, list):
    global error_content
    print("%s == %s" % (error_content, list))
    assert str(error_content) == str(list)