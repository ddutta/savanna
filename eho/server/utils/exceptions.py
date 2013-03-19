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


class ClusterOperationException(Exception):
    def __init__(self):
        self.error_code = "CLUSTER_OPERATION_ERROR"


class NotExistedNodeTypeException(ClusterOperationException):
    def __init__(self, value):
        self.value = value
        self.error_code = "NODE_TYPE_NOT_FOUND"

    def __str__(self):
        return repr("Cannot find NodeType %s" % self.value)


class ClusterNameExistedException(ClusterOperationException):
    def __init__(self, value):
        self.value = value
        self.error_code = "CLUSTER_NAME_NOT_EXISTED"

    def __str__(self):
        return repr("Cluster with name %s is already existed" % self.value)


class NotSingleNameNodeException(ClusterOperationException):
    def __init__(self, nn_count):
        self.nn_count = nn_count
        self.error_code = "NOT_SINGLE_NAME_NODE"

    def __str__(self):
        return repr(
            "Hadoop cluster should contain only 1 NameNode. "
            "Actual NN count is %s " % self.nn_count)


class NotSingleJobTrackerException(ClusterOperationException):
    def __init__(self, jt_count):
        self.jt_count = jt_count
        self.error_code = "NOT_SINGLE_JOB_TRACKER"

    def __str__(self):
        return repr(
            "Hadoop cluster should contain only 1 JobTracker. "
            "Actual JT count is %s " % self.jt_count)
