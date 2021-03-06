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

from oslo.config import cfg

from savanna.storage.models import NodeProcess, NodeProcessProperty, \
    NodeType, NodeTemplate, NodeTemplateConfig, Cluster, ClusterNodeCount
from savanna.storage.storage import DB
from savanna.openstack.common import log as logging

LOG = logging.getLogger(__name__)

CONF = cfg.CONF
CONF.import_opt('reset_db', 'savanna.config')
CONF.import_opt('stub_data', 'savanna.config')


def create_node_process(name, properties):
    """
    Creates new node process and node process properties
    :param name: process name
    :param properties: array of triples (name, required, default)
    :return: created node process
    """
    process = NodeProcess(name)
    DB.session.add(process)
    DB.session.commit()
    for p in properties:
        prop = NodeProcessProperty(process.id, p[0], p[1], p[2])
        DB.session.add(prop)
    DB.session.commit()
    return process


def create_node_type(name, processes):
    """
    Creates new node type using specified list of processes
    :param name:
    :param processes:
    :return:
    """
    node_type = NodeType(name)
    node_type.processes = processes
    DB.session.add(node_type)
    DB.session.commit()
    return node_type


def create_node_template(name, node_type_id, tenant_id, flavor_id, configs):
    """
    Creates new node templates
    :param name: template name
    :param node_type_id: node type
    :param tenant_id: tenant
    :param flavor_id: flavor
    :param configs: dict of process->property->value
    :return: created node template
    """
    node_template = NodeTemplate(name, node_type_id, tenant_id, flavor_id)
    DB.session.add(node_template)
    for process_name in configs:
        process = NodeProcess.query.filter_by(name=process_name).first()
        conf = configs.get(process_name)
        for prop in process.node_process_properties:
            val = conf.get(prop.name, None)
            if not val and prop.required:
                if not prop.default:
                    raise RuntimeError('Template \'%s\', value missed '
                                       'for required param: %s %s'
                                       % (name, process.name, prop.name))
                val = prop.default
            DB.session.add(NodeTemplateConfig(node_template.id, prop.id, val))
    DB.session.commit()

    return node_template


def create_cluster(name, base_image_id, tenant_id, templates):
    """
    Creates new cluster
    :param name: cluster name
    :param base_image_id: base image
    :param tenant_id: tenant
    :param templates: dict of template->count
    :return: created cluster
    """
    cluster = Cluster(name, base_image_id, tenant_id)
    DB.session.add(cluster)
    for template in templates:
        count = templates.get(template)
        cnc = ClusterNodeCount(cluster.id,
                               NodeTemplate.query.filter_by(name=template)
                               .first().id, int(count))
        DB.session.add(cnc)
    DB.session.commit()

    return cluster


def setup_defaults():
    nt_jt_nn = None
    nt_jt = None
    nt_nn = None
    nt_tt_dn = None

    if CONF.reset_db:
        # setup default processes
        p_jt = create_node_process('job_tracker', [('heap_size', True, None)])
        p_nn = create_node_process('name_node', [('heap_size', True, None)])
        p_tt = create_node_process('task_tracker', [('heap_size', True, None)])
        p_dn = create_node_process('data_node', [('heap_size', True, None)])

        for p in [p_jt, p_nn, p_tt, p_dn]:
            LOG.info('New NodeProcess: \'%s\'', p.name)

        # setup default node types
        nt_jt_nn = create_node_type('JT+NN', [p_jt, p_nn])
        nt_jt = create_node_type('JT', [p_jt])
        nt_nn = create_node_type('NN', [p_nn])
        nt_tt_dn = create_node_type('TT+DN', [p_tt, p_dn])

        for nt in [nt_jt_nn, nt_jt, nt_nn, nt_tt_dn]:
            LOG.info('New NodeType: \'%s\' %s',
                     nt.name, [p.name.__str__() for p in nt.processes])

    if CONF.stub_data:
        _setup_stub_data(nt_jt_nn, nt_jt, nt_nn, nt_tt_dn)


def _setup_stub_data(nt_jt_nn, nt_jt, nt_nn, nt_tt_dn):
    jt_nn_small = create_node_template('jt_nn.small', nt_jt_nn.id, 'tenant-01',
                                       'm1.small',
                                       {
                                           'job_tracker': {
                                               'heap_size': '896'
                                           },
                                           'name_node': {
                                               'heap_size': '896'
                                           }
                                       })
    jt_nn_medium = create_node_template('jt_nn.medium', nt_jt_nn.id,
                                        'tenant-01', 'm1.medium',
                                        {
                                            'job_tracker': {
                                                'heap_size': '1792'
                                            },
                                            'name_node': {
                                                'heap_size': '1792'
                                            }
                                        })
    jt_small = create_node_template('jt.small', nt_jt.id, 'tenant-01',
                                    'm1.small',
                                    {
                                        'job_tracker': {
                                            'heap_size': '1792'
                                        }
                                    })
    jt_medium = create_node_template('jt.medium', nt_jt.id, 'tenant-01',
                                     'm1.medium',
                                     {
                                         'job_tracker': {
                                             'heap_size': '3712'
                                         }
                                     })
    nn_small = create_node_template('nn.small', nt_nn.id, 'tenant-01',
                                    'm1.small',
                                    {
                                        'name_node': {
                                            'heap_size': '1792'
                                        }
                                    })
    nn_medium = create_node_template('nn.medium', nt_nn.id, 'tenant-01',
                                     'm1.medium',
                                     {
                                         'name_node': {
                                             'heap_size': '3712'
                                         }
                                     })
    tt_dn_small = create_node_template('tt_dn.small', nt_tt_dn.id, 'tenant-01',
                                       'm1.small',
                                       {
                                           'task_tracker': {
                                               'heap_size': '896'
                                           },
                                           'data_node': {
                                               'heap_size': '896'
                                           }
                                       })
    tt_dn_medium = create_node_template('tt_dn.medium', nt_tt_dn.id,
                                        'tenant-01',
                                        'm1.medium',
                                        {
                                            'task_tracker': {
                                                'heap_size': '1792'
                                            },
                                            'data_node': {
                                                'heap_size': '1792'
                                            }
                                        })

    for tmpl in [jt_nn_small, jt_nn_medium, jt_small, jt_medium, nn_small,
                 nn_medium, tt_dn_small, tt_dn_medium]:
        LOG.info('New NodeTemplate: %s \'%s\' %s',
                 tmpl.id, tmpl.name, tmpl.flavor_id)

    LOG.info('All defaults has been inserted')
