@tags @tag
Feature: Test of template section

    Scenario: User can see templates
        When User see templates
        Then Response is "200"
        #And Response list of list node_templates:"[u'jt_nn.small', u'jt_nn.medium', u'jt.small', u'jt.medium', u'nn.small', u'nn.medium', u'tt_dn.small', u'tt_dn.medium']"

    Scenario: User can create template
        Given node_template body
        """
        {
            "node_template": {
                "name": "custom_user_template",
                "node_type": "TT+DN",
                "flavor_id": "m1.medium",
                "task_tracker": {
                    "heap_size": 384,
                    "max_map_tasks": 3,
                    "max_reduce_tasks": 1,
                    "task_heap_size": 640
                },
                "data_node": {
                    "heap_size": 384
                }
            }
        }
        """
        When User create template
        Then Response is "202"

    Scenario: User can get templates
        When User see templates
        Then Response is "200"
        #And Response list of list node_templates:"[u'jt_nn.small', u'jt_nn.medium', u'jt.small', u'jt.medium', u'nn.small', u'nn.medium', u'tt_dn.small', u'tt_dn.medium', u'QA_n_n']"

    Scenario: User can get template by id
        When User get template with id: "0"
        Then Response is "200"
        #And Response for list node_template by id is:"{u'name_node': {u'heap_size': u'512'}, u'node_type': {u'processes': [u'name_node'], u'name': u'NN'}, u'flavor_id': u'm1.tiny', u'name': u'QA_n_n'}"

    Scenario: User can delete template
        When User delete template with id: "0"
        Then Response is "204"

    Scenario: User can get templates
         When User see templates
         Then Response is "200"
         #And Response list of list node_templates:"[u'jt_nn.small', u'jt_nn.medium', u'jt.small', u'jt.medium', u'nn.small', u'nn.medium', u'tt_dn.small', u'tt_dn.medium']"