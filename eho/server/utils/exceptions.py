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

from eho.openstack.common.exception import ApiError


class NotExistedNodeTypeException(ApiError):
    def __init__(self, value):
        self.message = "Cannot find NodeType %s" % value
        self.code = "NODE_TYPE_NOT_FOUND"

    def __str__(self):
        return repr(self.message)


class ClusterNameExistedException(ApiError):
    def __init__(self, value):
        self.message = "Cluster with name %s is already existed" % value
        self.code = "CLUSTER_NAME_NOT_EXISTED"

    def __str__(self):
        return repr(self.message)


class NotSingleNameNodeException(ApiError):
    def __init__(self, nn_count):
        self.message = "Hadoop cluster should contain only 1 NameNode. " \
                       "Actual NN count is %s " % nn_count
        self.code = "NOT_SINGLE_NAME_NODE"

    def __str__(self):
        return repr(self.message)


class NotSingleJobTrackerException(ApiError):
    def __init__(self, jt_count):
        self.message = "Hadoop cluster should contain only 1 JobTracker. " \
                       "Actual JT count is %s " % jt_count
        self.code = "NOT_SINGLE_JOB_TRACKER"

    def __str__(self):
        return repr(self.message)
