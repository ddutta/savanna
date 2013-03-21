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

import json
import logging
import tempfile
import unittest
import uuid
import os

import eventlet

from eho.server import scheduler
from eho.server.main import make_app
from eho.server.service import api
from eho.server.storage.models import Node, NodeTemplate
from eho.server.storage.storage import DB
import eho.server.main


def _stub_vm_creation_job(template_id):
    template = NodeTemplate.query.filter_by(id=template_id).first()
    eventlet.sleep(2)
    return 'ip-address', uuid.uuid4().hex, template.id


def _stub_launch_cluster(headers, cluster):
    logging.debug('stub launch_cluster called with %s, %s', headers, cluster)
    pile = eventlet.GreenPile(scheduler.POOL)

    for elem in cluster.node_counts:
        node_count = elem.count
        for _ in xrange(0, node_count):
            pile.spawn(_stub_vm_creation_job, elem.node_template_id)

    for (ip, vm_id, elem) in pile:
        DB.session.add(Node(vm_id, cluster.id, elem))
        logging.debug("VM '%s/%s/%s' created", ip, vm_id, elem)


def _stub_stop_cluster(headers, cluster):
    logging.debug("stub stop_cluster called with %s, %s", headers, cluster)


def _stub_auth_token(*args, **kwargs):
    logging.debug('stub token filter called with %s, %s', args, kwargs)

    def _filter(app):
        def _handler(env, start_response):
            return app(env, start_response)

        return _handler

    return _filter


def _stub_auth_valid(*args, **kwargs):
    logging.debug('stub token validation called with %s, %s', args, kwargs)

    def _filter(app):
        def _handler(env, start_response):
            return app(env, start_response)

        return _handler

    return _filter


class TestApi(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.maxDiff = 10000

        # store functions that will be stubbed
        self._prev_auth_token = eho.server.main.auth_token
        self._prev_auth_valid = eho.server.main.auth_valid
        self._prev_cluster_launch = api.cluster_ops.launch_cluster
        self._prev_cluster_stop = api.cluster_ops.stop_cluster

        # stub functions
        eho.server.main.auth_token = _stub_auth_token
        eho.server.main.auth_valid = _stub_auth_valid
        api.cluster_ops.launch_cluster = _stub_launch_cluster
        api.cluster_ops.stop_cluster = _stub_stop_cluster

        app = make_app(
            TESTING=True,
            RESET_DB=True,
            STUB_DATA=True,
            LOG_LEVEL="DEBUG",
            ALLOW_CLUSTER_OPS=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///' + self.db_path,
            SQLALCHEMY_ECHO=False,
            OS_AUTH_HOST='localhost',
            OS_AUTH_PORT='12345',
            OS_AUTH_PROTOCOL='http',
            OS_ADMIN_USER='admin',
            OS_ADMIN_PASSWORD='admin',
            OS_ADMIN_TENANT='admin'
        )
        logging.debug('Test db path: %s', self.db_path)
        logging.debug('Test app.config: %s', app.config)

        self.app = app.test_client()

    def tearDown(self):
        # unstub functions
        eho.server.main.auth_token = self._prev_auth_token
        eho.server.main.auth_valid = self._prev_auth_valid
        api.cluster_ops.launch_cluster = self._prev_cluster_launch
        api.cluster_ops.stop_cluster = self._prev_cluster_stop

        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_list_node_templates(self):
        rv = self.app.get('/v0.2/some-tenant-id/node-templates.json')
        self.assertEquals(rv.status_code, 200)
        data = json.loads(rv.data)

        # clean all ids
        for idx in xrange(0, len(data.get(u'node_templates'))):
            del data.get(u'node_templates')[idx][u'id']

        self.assertEquals(data, _get_templates_stub_data())

    def test_create_node_template(self):
        rv = self.app.post('/v0.2/some-tenant-id/node-templates.json',
                           data=json.dumps(dict(
                               node_template=dict(
                                   name='test_template',
                                   node_type='JT+NN',
                                   flavor_id='test_flavor',
                                   job_tracker={
                                       'heap_size': '1234'
                                   },
                                   name_node={
                                       'heap_size': '2345'
                                   }
                               ))))
        self.assertEquals(rv.status_code, 202)
        data = json.loads(rv.data)

        data = data['node_template']

        # clean all ids
        del data[u'id']

        self.assertEquals(data, {
            u'job_tracker': {
                u'heap_size': u'1234'
            }, u'name': u'test_template',
            u'node_type': {
                u'processes': [
                    u'job_tracker', u'name_node'
                ],
                u'name': u'JT+NN'
            },
            u'flavor_id': u'test_flavor',
            u'name_node': {
                u'heap_size': u'2345'
            }
        })

    def test_list_clusters(self):
        rv = self.app.get('/v0.2/some-tenant-id/clusters.json')
        self.assertEquals(rv.status_code, 200)
        data = json.loads(rv.data)

        self.assertEquals(data, {
            u'clusters': []
        })

    def test_create_clusters(self):
        rv = self.app.post('/v0.2/some-tenant-id/clusters.json',
                           data=json.dumps(dict(
                               cluster=dict(
                                   name='test-cluster',
                                   base_image_id='base-image-id',
                                   node_templates={
                                       'jt_nn.medium': 1,
                                       'tt_dn.small': 5
                                   }
                               ))))
        self.assertEquals(rv.status_code, 202)
        data = json.loads(rv.data)

        data = data['cluster']

        cluster_id = data.pop(u'id')

        self.assertEquals(data, {
            u'status': u'Starting',
            u'service_urls': {},
            u'name': u'test-cluster',
            u'base_image_id': u'base-image-id',
            u'node_templates': {
                u'jt_nn.medium': 1,
                u'tt_dn.small': 5
            },
            u'nodes': []
        })

        eventlet.sleep(4)

        rv = self.app.get('/v0.2/some-tenant-id/clusters/%s.json' % cluster_id)
        self.assertEquals(rv.status_code, 200)
        data = json.loads(rv.data)

        data = data['cluster']

        self.assertEquals(data.pop(u'id'), cluster_id)

        # clean all ids
        for idx in xrange(0, len(data.get(u'nodes'))):
            del data.get(u'nodes')[idx][u'vm_id']
            del data.get(u'nodes')[idx][u'node_template'][u'id']

        nodes = data.pop(u'nodes')

        self.assertEquals(data, {
            u'status': u'Active',
            u'service_urls': {},
            u'name': u'test-cluster',
            u'base_image_id': u'base-image-id',
            u'node_templates': {
                u'jt_nn.medium': 1,
                u'tt_dn.small': 5
            }
        })

        self.assertEquals(_sorted_nodes(nodes), _sorted_nodes([
            {u'node_template': {u'name': u'tt_dn.small'}},
            {u'node_template': {u'name': u'tt_dn.small'}},
            {u'node_template': {u'name': u'tt_dn.small'}},
            {u'node_template': {u'name': u'tt_dn.small'}},
            {u'node_template': {u'name': u'tt_dn.small'}},
            {u'node_template': {u'name': u'jt_nn.medium'}}
        ]))

    def test_delete_node_template(self):
        rv = self.app.post('/v0.2/some-tenant-id/node-templates.json',
                           data=json.dumps(dict(
                               node_template=dict(
                                   name='test_template_2',
                                   node_type='JT+NN',
                                   flavor_id='test_flavor_2',
                                   job_tracker={
                                       'heap_size': '1234'
                                   },
                                   name_node={
                                       'heap_size': '2345'
                                   }
                               ))))
        self.assertEquals(rv.status_code, 202)
        data = json.loads(rv.data)

        data = data['node_template']

        node_template_id = data.pop(u'id')

        rv = self.app.get(
            '/v0.2/some-tenant-id/node-templates/%s.json' % node_template_id)
        self.assertEquals(rv.status_code, 200)
        data = json.loads(rv.data)

        data = data['node_template']

        # clean all ids
        del data[u'id']

        self.assertEquals(data, {
            u'job_tracker': {
                u'heap_size': u'1234'
            }, u'name': u'test_template_2',
            u'node_type': {
                u'processes': [
                    u'job_tracker', u'name_node'
                ],
                u'name': u'JT+NN'
            },
            u'flavor_id': u'test_flavor_2',
            u'name_node': {
                u'heap_size': u'2345'
            }
        })

        rv = self.app.delete(
            '/v0.2/some-tenant-id/node-templates/%s.json' % node_template_id)
        self.assertEquals(rv.status_code, 204)

        rv = self.app.get(
            '/v0.2/some-tenant-id/node-templates/%s.json' % node_template_id)

        # todo(vrovachev): change success code to 404
        self.assertEquals(rv.status_code, 500)

    def test_delete_cluster(self):
        rv = self.app.post('/v0.2/some-tenant-id/clusters.json',
                           data=json.dumps(dict(
                               cluster=dict(
                                   name='test-cluster-2',
                                   base_image_id='base-image-id_2',
                                   node_templates={
                                       'jt_nn.medium': 1,
                                       'tt_dn.small': 5
                                   }
                               ))))
        self.assertEquals(rv.status_code, 202)
        data = json.loads(rv.data)

        data = data['cluster']

        cluster_id = data.pop(u'id')

        rv = self.app.get('/v0.2/some-tenant-id/clusters/%s.json' % cluster_id)
        self.assertEquals(rv.status_code, 200)
        data = json.loads(rv.data)

        data = data['cluster']

        # delete all ids
        del data[u'id']

        self.assertEquals(data, {
            u'status': u'Starting',
            u'service_urls': {},
            u'name': u'test-cluster-2',
            u'base_image_id': u'base-image-id_2',
            u'node_templates': {
                u'jt_nn.medium': 1,
                u'tt_dn.small': 5
            },
            u'nodes': []
        })

        rv = self.app.delete(
            '/v0.2/some-tenant-id/clusters/%s.json' % cluster_id)
        self.assertEquals(rv.status_code, 204)

        eventlet.sleep(1)

        rv = self.app.get('/v0.2/some-tenant-id/clusters/%s.json' % cluster_id)

        # todo(vrovachev): change success code to 404
        self.assertEquals(rv.status_code, 500)


def _sorted_nodes(nodes):
    return sorted(nodes, key=lambda elem: elem[u'node_template'][u'name'])


def _get_templates_stub_data():
    return {
        u'node_templates': [
            {
                u'job_tracker': {
                    u'heap_size': u'896'
                },
                u'name': u'jt_nn.small',
                u'node_type': {
                    u'processes': [
                        u'job_tracker', u'name_node'
                    ],
                    u'name': u'JT+NN'
                },
                u'flavor_id': u'm1.small',
                u'name_node': {
                    u'heap_size': u'896'
                }
            },
            {
                u'job_tracker': {
                    u'heap_size': u'1792'
                },
                u'name': u'jt_nn.medium',
                u'node_type': {
                    u'processes': [
                        u'job_tracker', u'name_node'
                    ], u'name': u'JT+NN'
                },
                u'flavor_id': u'm1.medium',
                u'name_node': {
                    u'heap_size': u'1792'
                }
            },
            {
                u'job_tracker': {
                    u'heap_size': u'1792'
                },
                u'name': u'jt.small',
                u'node_type': {
                    u'processes': [
                        u'job_tracker'
                    ],
                    u'name': u'JT'
                },
                u'flavor_id': u'm1.small'
            },
            {
                u'job_tracker': {
                    u'heap_size': u'3712'
                },
                u'name': u'jt.medium',
                u'node_type': {
                    u'processes': [
                        u'job_tracker'
                    ],
                    u'name': u'JT'},
                u'flavor_id': u'm1.medium'
            },
            {
                u'name': u'nn.small',
                u'node_type': {
                    u'processes': [
                        u'name_node'
                    ],
                    u'name': u'NN'
                },
                u'flavor_id': u'm1.small',
                u'name_node': {
                    u'heap_size': u'1792'
                }
            },
            {
                u'name': u'nn.medium',
                u'node_type': {
                    u'processes': [
                        u'name_node'
                    ],
                    u'name': u'NN'
                },
                u'flavor_id': u'm1.medium',
                u'name_node': {
                    u'heap_size': u'3712'
                }
            },
            {
                u'name': u'tt_dn.small',
                u'task_tracker': {
                    u'heap_size': u'896'
                },
                u'data_node': {
                    u'heap_size': u'896'
                },
                u'node_type': {
                    u'processes': [
                        u'task_tracker', u'data_node'
                    ],
                    u'name': u'TT+DN'
                },
                u'flavor_id': u'm1.small'
            },
            {
                u'name': u'tt_dn.medium',
                u'task_tracker': {
                    u'heap_size': u'1792'
                },
                u'data_node': {
                    u'heap_size': u'1792'
                },
                u'node_type': {
                    u'processes': [
                        u'task_tracker', u'data_node'
                    ],
                    u'name': u'TT+DN'
                },
                u'flavor_id': u'm1.medium'
            }
        ]
    }


if __name__ == '__main__':
    unittest.main()
