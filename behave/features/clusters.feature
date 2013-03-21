@tags @tag
Feature: Test of cluster section

    Scenario: User can get clusters
        When  User see clusters
        Then  Response is "200"
        #And Response list of list clusters:"[u'hadoop']"

    Scenario: User can create cluster
        Given cluster data
        """
        {"cluster": {"node_templates": {"jt_nn.medium": 1, "tt_dn.small": 1}, "name": "QAcluster", "base_image_id": "d9342ba8-4c51-441c-8d5b-f9e14a901299"}}
        """
        When User create cluster
        Then  Response is "202"

    Scenario: User can create cluster
        Given cluster data
        """
        {"cluster": {"node_templates": {"jt_nn.medium": "1", "tt_dn.small": "1"}, "name": "QAcluster2", "base_image_id": "d9342ba8-4c51-441c-8d5b-f9e14a901299"}}
        """
        When User create cluster
        Then  Response is "400"
        And Error content:"{u'error_name': u'VALIDATION_ERROR', u'error_message': u"u'1' is not of type 'integer'", u'error_code': 400}"

    Scenario: User can get clusters
        When  User see clusters
        Then  Response is "200"
        #And Response list of list clusters:"[u'hadoop', u'QAcluster']"

    Scenario: User can get cluster by ID
        When User get cluster with id: "0"
        Then  Response is "200"
        #And Response for list cluster by id is:"{u'status': u'Starting', u'service_urls': {}, u'name': u'QAcluster', u'base_image_id': u'd9342ba8-4c51-441c-8d5b-f9e14a901299', u'node_templates': {u'jt_nn.medium': 1, u'tt_dn.small': 1}, u'nodes': []}"

    Scenario: User can delete cluster by ID
        When User delete cluster with id: "0"
        Then  Response is "204"

    Scenario: User can get clusters
        When  User see clusters
        Then  Response is "200"
        #And Response list of list clusters:"[u'hadoop']"
