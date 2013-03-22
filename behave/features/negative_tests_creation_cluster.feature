@tags @tag
Feature: Negative tests of cluster section

    Scenario: User can create cluster with name "QA-cluster"
        Given cluster data
        """
        {"cluster": {"node_templates": {"jt_nn.medium": 1, "tt_dn.small": 1}, "name": "QA-cluster", "base_image_id": "d9342ba8-4c51-441c-8d5b-f9e14a901299"}}
        """
        When User create cluster
        Then  Response is "202"

    Scenario: User can create cluster with blank cluster name
        Given cluster data
        """
        {"cluster": {"node_templates": {"jt_nn.medium": 1, "tt_dn.small": 1}, "name": "", "base_image_id": "d9342ba8-4c51-441c-8d5b-f9e14a901299"}}
        """
        When User create cluster
        Then  Response is "400"

    Scenario: User can create cluster with name "QA-cluster" that already exists
        Given cluster data
        """
        {"cluster": {"node_templates": {"jt_nn.medium": 1, "tt_dn.small": 1}, "name": "QA-cluster", "base_image_id": "d9342ba8-4c51-441c-8d5b-f9e14a901299"}}
        """
        When  User create cluster
        Then  Response is "400"

    Scenario: User can create cluster with invalid characters in cluster name
        Given cluster data
        """
        {"cluster": {"node_templates": {"jt_nn.medium": 1, "tt_dn.small": 1}, "name": "QA_*&cluster", "base_image_id": "d9342ba8-4c51-441c-8d5b-f9e14a901299"}}
        """
        When  User create cluster
        Then  Response is "400"

    Scenario: User can create cluster with space in cluster name
        Given cluster data
        """
        {"cluster": {"node_templates": {"jt_nn.medium": 1, "tt_dn.small": 1}, "name": "QA cluster", "base_image_id": "d9342ba8-4c51-441c-8d5b-f9e14a901299"}}
        """
        When  User create cluster
        Then  Response is "400"

    Scenario: User can create cluster with blank base image ID
        Given cluster data
        """
        {"cluster": {"node_templates": {"jt_nn.medium": 1, "tt_dn.small": 1}, "name": "QA-cluster-1", "base_image_id": ""}}
        """
        When  User create cluster
        Then  Response is "400"

    Scenario: User can create cluster with wrong base image ID #This cluster create #No validation
        #Given cluster data
        #"""
        #{"cluster": {"node_templates": {"jt_nn.medium": 1, "tt_dn.small": 1}, "name": "QA-cluster-2", "base_image_id": "abc"}}
        #"""
        #When  User create cluster
        #Then  Response is "400"

    Scenario: User can create cluster with negative parameter in number of jt_nn
        Given cluster data
        """
        {"cluster": {"node_templates": {"jt_nn.medium": -1, "tt_dn.small": 1}, "name": "QA-cluster-3", "base_image_id": "d9342ba8-4c51-441c-8d5b-f9e14a901299"}}
        """
        When  User create cluster
        Then  Response is "400"

    Scenario: User can create cluster with negative parameter in number of tt_dn
        Given cluster data
        """
        {"cluster": {"node_templates": {"jt_nn.medium": 1, "tt_dn.small": -1}, "name": "QA-cluster-4", "base_image_id": "d9342ba8-4c51-441c-8d5b-f9e14a901299"}}
        """
        When  User create cluster
        Then  Response is "400"

    Scenario: User can create cluster with characters in number of jt_nn #No validation
        #Given cluster data
        #"""
        #{"cluster": {"node_templates": {"jt_nn.medium": abc, "tt_dn.small": 1}, "name": "QA-cluster-5", "base_image_id": "d9342ba8-4c51-441c-8d5b-f9e14a901299"}}
        #"""
        #When  User create cluster
        #Then  Response is "400"

    Scenario: User can create cluster with characters in number of tt_dn #No validation
        #Given cluster data
        #"""
        #{"cluster": {"node_templates": {"jt_nn.medium": 1, "tt_dn.small": abc}, "name": "QA-cluster-6", "base_image_id": "d9342ba8-4c51-441c-8d5b-f9e14a901299"}}
        #"""
        #When  User create cluster
        #Then  Response is "400"

    Scenario: User can create cluster with nonexistent JT and NN
        Given cluster data
        """
        {"cluster": {"node_templates": {"abc": 1, "tt_dn.small": 1}, "name": "QA-cluster-7", "base_image_id": "d9342ba8-4c51-441c-8d5b-f9e14a901299"}}
        """
        When  User create cluster
        Then  Response is "400"

    Scenario: User can create cluster with nonexistent TT and DN
        Given cluster data
        """
        {"cluster": {"node_templates": {"jt_nn.medium": 1, "abc": 1}, "name": "QA-cluster-8", "base_image_id": "d9342ba8-4c51-441c-8d5b-f9e14a901299"}}
        """
        When  User create cluster
        Then  Response is "400"

    Scenario: User can create cluster with empty value for JT and NN
        Given cluster data
        """
        {"cluster": {"node_templates": {"": 1, "tt_dn.small": 1}, "name": "QA-cluster-9", "base_image_id": "d9342ba8-4c51-441c-8d5b-f9e14a901299"}}
        """
        When  User create cluster
        Then  Response is "400"

    Scenario: User can create cluster with empty value for TT and DN
        Given cluster data
        """
        {"cluster": {"node_templates": {"jt_nn.medium": 1, "": 1}, "name": "QA-cluster-10", "base_image_id": "d9342ba8-4c51-441c-8d5b-f9e14a901299"}}
        """
        When  User create cluster
        Then  Response is "400"