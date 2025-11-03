# Installing the base ACM - using the CLI

Note: The ACM stack needs resources - on a single node, while CPU with 8 cores is sufficient for the installation, memory with 24 GB is too low !

## 1. Install the operator

Note: best practice is to use namespace `open-cluster-management` if it's available.

Create the namespace and switch to it.

```
[focs@BM-OCP3-gateway ~]$ oc create namespace open-cluster-management
namespace/open-cluster-management created
[focs@BM-OCP3-gateway ~]$ oc project open-cluster-management
Now using project "open-cluster-management" on server "https://api.acm-ocp03.single.demo.local:6443".
[focs@BM-OCP3-gateway ~]$
```

Create the operator group - the name is arbitrary and follows usually the project name with a postfix of an arbitrary string (if automatically generated through the console based intsallation of the operator), like here in `og-acm.yaml`. Note that there is no configuration specified - all the defaults will be installed and configured:

```
!!!include(og-acm.yaml)!!!
```

Apply the operator group definition:

```
[focs@BM-OCP3-gateway install-acm]$ oc apply -f og-acm.yaml
operatorgroup.operators.coreos.com/open-cluster-management-myog created
[focs@BM-OCP3-gateway install-acm]$
```

Create the subscription, like in `acm-operator-subscription.yaml`:

```
!!!include(acm-operator-subscription.yaml)!!!
```

Apply the subscription:

```
[focs@BM-OCP3-gateway install-acm]$ oc apply -f acm-operator-subscription.yaml
subscription.operators.coreos.com/advanced-cluster-management created
[focs@BM-OCP3-gateway install-acm]$
```

Check for the subscription to be applied:

```
[focs@BM-OCP3-gateway install-acm]$ oc get clusterserviceversion
NAME                                  DISPLAY                                      VERSION   REPLACES   PHASE
advanced-cluster-management.v2.14.0   Advanced Cluster Management for Kubernetes   2.14.0               Succeeded
[focs@BM-OCP3-gateway install-acm]$
```

Create the MultiClusterHub resource like in `acm-multiclusterhub-instance.yaml`:

```
!!!include(acm-multiclusterhub-instance.yaml)!!!
```

Apply the resource and check for the status until it switches from "Installing" to "Ready":

```
[focs@BM-OCP3-gateway install-acm]$ oc apply -f acm-multiclusterhub-instance.yaml
multiclusterhub.operator.open-cluster-management.io/multiclusterhub created
[focs@BM-OCP3-gateway install-acm]$
[focs@BM-OCP3-gateway install-acm]$ oc  get -nopen-cluster-management multiclusterhub/multiclusterhub
NAME              STATUS       AGE   CURRENTVERSION   DESIREDVERSION
multiclusterhub   Installing   40s                    2.14.0
[focs@BM-OCP3-gateway install-acm]$
```

## PArking lot

Once the operator is installed, an instance of the `MultiClusterHub` resource must be created. There are no configurables for it in normal virtualization. Only if one want's to use it in edge fleet management, the edge-manager-preview and siteconfig (optional) might be required. Hopwever, the most of the functionality is enabled by default. ([see](https://docs.redhat.com/en/documentation/red_hat_advanced_cluster_management_for_kubernetes/2.14/html-single/install/index#component-config))
![UI view of OpenShift console to create UDNs](images/acm-configure-multicluster-instance.png)

Note: As ACM is supported also on infra nodes and ---> node selector
