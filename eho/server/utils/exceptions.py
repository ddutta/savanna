class NotExistedNodeTypeException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr("Cannot find NodeType %s" % self.value)


class ClusterNameExistedException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr("Cluster with name %s is already existed" % self.value)


class NotSingleNameNodeException(Exception):
    def __init__(self, nn_count):
        self.nn_count = nn_count

    def __str__(self):
        return repr(
            "Hadoop cluster should contain only 1 NameNode. "
            "Actual NN count is %s " % self.nn_count)


class NotSingleJobTrackerException(Exception):
    def __init__(self, jt_count):
        self.jt_count = jt_count

    def __str__(self):
        return repr(
            "Hadoop cluster should contain only 1 JobTracker. "
            "Actual JT count is %s " % self.jt_count)
