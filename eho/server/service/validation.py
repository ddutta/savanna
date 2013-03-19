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

from jsonschema import validate
from eho.server.service import api
import eho.server.utils.exceptions as exceptions


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

    validate(values, schema)

    #check that requested cluster name is unique
    unique_names = [cluster.name for cluster in api.get_clusters()]
    if values['name'] in unique_names:
        raise exceptions.ClusterNameExistedException(values['name'])

    #check that requested templates are from already defined values
    node_templates = values['node_templates']
    possible_node_types = [nt.name for nt in api.get_node_templates()]
    for nt in node_templates:
        if nt not in possible_node_types:
            raise exceptions.NotExistedNodeTypeException(nt)
            #check node count is integer and non-zero value
        validate(node_templates[nt], {"type": "integer", "minimum": 1})

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
        raise exceptions.NotSingleNameNodeException(nn_count)

    if jt_count != 1:
        raise exceptions.NotSingleJobTrackerException(jt_count)
