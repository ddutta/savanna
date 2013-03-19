# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from eho.server.service import api
from eho.server.utils.api import request_data, abort_and_log, render
import jsonschema
from eho.server.utils.exceptions import ApiError, \
    ClusterNameExistedException, NotExistedNodeTypeException, \
    NotSingleJobTrackerException, NotSingleNameNodeException


def validate(validate_func):
    def decorator(func):
        def handler(*args, **kwargs):
            try:
                validate_func(request_data())
            except jsonschema.ValidationError, e:
                abort_and_log(400,
                              "Validation error while adding new cluster: %s"
                              % str(e), e)
            except ApiError, e:
                return bad_request(e)
            except Exception, e:
                abort_and_log(500, "Exception while adding new Cluster", e)

            return func(*args, **kwargs)

        return handler

    return decorator


def bad_request(error):
    message = {
        "error_code": 400,
        "error_message": error.message,
        "error_name": error.code
    }
    resp = render(message)
    resp.status_code = 400

    return resp


def validate_cluster_create(cluster_values):
    values = cluster_values['cluster']

    #base validation schema of cluster creation operation
    schema = {
        "title": "Cluster creation schema",
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 1, "pattern": "^\S*$"},
            "base_image_id": {"type": "string", "minLength": 1},
            "node_templates": {
                "type": "object"
            }
        },
        "required": ["name", "base_image_id", "node_templates"]
    }

    jsonschema.validate(values, schema)

    #check that requested cluster name is unique
    unique_names = [cluster.name for cluster in api.get_clusters()]
    if values['name'] in unique_names:
        raise ClusterNameExistedException(values['name'])

    #check that requested templates are from already defined values
    node_templates = values['node_templates']
    possible_node_types = [nt.name for nt in api.get_node_templates()]
    for nt in node_templates:
        if nt not in possible_node_types:
            raise NotExistedNodeTypeException(nt)
            #check node count is integer and non-zero value
        jsonschema.validate(node_templates[nt],
                            {"type": "integer", "minimum": 1})

    #check that requested cluster contains only 1 instance of NameNode
    # and 1 instance of JobTracker
    jt_count = 0
    nn_count = 0

    for nt_name in node_templates:
        processes = api.get_node_template(name=nt_name).dict['node_type'][
            'processes']
        if "job_tracker" in processes:
            jt_count += node_templates[nt_name]
        if "name_node" in processes:
            nn_count += node_templates[nt_name]

    if nn_count != 1:
        raise NotSingleNameNodeException(nn_count)

    if jt_count != 1:
        raise NotSingleJobTrackerException(jt_count)
