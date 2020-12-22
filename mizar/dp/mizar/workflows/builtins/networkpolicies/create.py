# SPDX-License-Identifier: MIT
# Copyright (c) 2020 The Authors.

# Authors: Hong Chang   <@Hong-Chang>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:The above copyright
# notice and this permission notice shall be included in all copies or
# substantial portions of the Software.THE SOFTWARE IS PROVIDED "AS IS",
# WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
from mizar.common.workflow import *
from mizar.common.kubernetes_util import *
from mizar.dp.mizar.operators.endpoints.endpoints_operator import *
from mizar.dp.mizar.operators.networkpolicies.networkpolicies_operator import *

endpoint_opr = EndpointOperator()
networkpolicy_opr = NetworkPolicyOperator()

logger = logging.getLogger()

class k8sNetworkPolicyCreate(WorkflowTask):
    def requires(self):
        logger.info("Requires {task}".format(task=self.__class__.__name__))
        return []

    def run(self):
        logger.info("Run {task}".format(task=self.__class__.__name__))
        
        name = self.param.name
        pod_label_dict = self.param.spec["podSelector"]["matchLabels"]
        policy_types = self.param.spec["policyTypes"]
        self.handle_networkpolicy_create_update(name, pod_label_dict, policy_types)

        self.finalize()

    def handle_networkpolicy_create_update(self, name, pod_label_dict, policy_types):
        pods = list_pods_by_labels(pod_label_dict)

        has_ingress = "Ingress" in policy_types
        has_egress = "Egress" in policy_types

        if not has_ingress and not has_egress:
            return

        for pod in pods.items:
            pod_name = pod.metadata.name
            eps = endpoint_opr.store.get_eps_in_pod(pod_name)
            for ep in eps.values():
                if has_ingress:
                    if name not in ep.ingress_networkpolicies:
                        ep.add_ingress_networkpolicy(name)
                    data_for_networkpolicy_ingress = self.generate_data_for_networkpolicy_ingress(ep)
                if has_egress:
                    if name not in ep.egress_networkpolicies:
                        ep.add_egress_networkpolicy(name)
                    data_for_networkpolicy_egress = self.generate_data_for_networkpolicy_egress(ep)
                data_for_networkpolicy = {
                    "old": {},
                    "ingress": data_for_networkpolicy_ingress,
                    "egress": data_for_networkpolicy_egress,
                }
                logger.info("data_for_networkpolicy: {}".format(data_for_networkpolicy))
                #TODO Send data from operator to daemon
                

    def generate_data_for_networkpolicy_ingress(self, ep):
        data = self.init_data_for_networkpolicy()
        #TODO build ingress data
        return data

    def generate_data_for_networkpolicy_egress(self, ep):
        data = self.init_data_for_networkpolicy()
        #TODO build egress data
        return data

    def init_data_for_networkpolicy(self):
        data = {
            "indexed_policy_count": 0,
            "networkpolicy_map": {},
            "cidrs_map_no_except": {},
            "cidrs_map_with_except": {},
            "cidrs_map_except": {},
            "ports_map": {},
            "cidr_and_policies_map_no_except": {},
            "cidr_and_policies_map_with_except": {},
            "cidr_and_policies_map_except": {},
            "port_and_policies_map": {},
            "indexed_policy_map": {},
            "cidr_table_no_except": [],
            "cidr_table_with_except": [],
            "cidr_table_except": [],
            "port_table": [],
        }
        return data
