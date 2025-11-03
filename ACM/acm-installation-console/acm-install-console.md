# Installing the base ACM - using the console

## 1. Install the operator

From Operator Hub, select the ACM and install it:

![UI view of OpenShift console to create UDNs](images/acm-install-operator.png)
![UI view of OpenShift console to create UDNs](images/acm-install-operator-start.png)

Configure the operator to use namespace `open-cluster-management`. The subscription can be chosen as wanted - but during a PoC, bets is to use manual approvals to avoid changes without knowing.
![UI view of OpenShift console to create UDNs](images/acm-configure-operator-namespace.png)

Once the operator is installed, an instance of the `MultiClusterHub` resource must be created. There are no configurables for it in normal virtualization. Only if one want's to use it in edge fleet management, the edge-manager-preview and siteconfig (optional) might be required. Hopwever, the most of the functionality is enabled by default. ([see](https://docs.redhat.com/en/documentation/red_hat_advanced_cluster_management_for_kubernetes/2.14/html-single/install/index#component-config))
![UI view of OpenShift console to create UDNs](images/acm-configure-multicluster-instance.png)

Note: As ACM is supported also on infra nodes and ---> node selector
