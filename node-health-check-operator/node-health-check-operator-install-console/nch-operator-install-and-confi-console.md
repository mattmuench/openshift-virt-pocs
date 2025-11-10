# Node Health Check operator installation and configuration using the CLI

**Important: in order to use any remediation techniques, the NHC operator must be installed.**

## Install operator from OperatorHub

![UI view of OpenShift OperatorHub](images/nhc-operator-install-operatorhub.png)
![UI view of OpenShift OperatorHUb NHC Version](images/nhc-operator-install-operator-version.png)
![UI view of OpenShift OperatorHUb NHC subscription](images/nhc-operator-install-operator-subscription.png)
![UI view of OpenShift OperatorHUb NHC installing](images/nhc-operator-install-installing.png)

**NOTE: Missing manual approval for operator installation**

![UI view of OpenShift OperatorHUb NHC ready](images/nhc-operator-install-ready.png)
![UI view of OpenShift OperatorHUb NHC ready](images/nhc-operator-installed-overview.png)

A NodehealthCheck instance must be created. There is a form view available:
![UI view of OpenShift OperatorHUb NHC ready](images/nhc-operator-instance-form-view.png)

## Install the operator

One doesn't ned to create a new namespace since the operator goes to openshift-operators that should be there anyways.

```
!!!include(nhc-operatorgroup.yaml)!!!
```

Create the operator group.

```
oc create -f nhc-operatorgroup.yaml
```

Create a a subscription.

```
!!!include(nhc-subscription.yaml)!!!
```

```
oc create -f nhc-subscription.yaml
```

Verify the installation.

```
# Check the ClusterServiceVersion (CSV) status
oc get csv -n openshift-operators | grep node-healthcheck-operator

# Wait for the PHASE to be 'Succeeded'
# Example Output: node-healthcheck-operator.vX.Y.Z Node Health Check Operator X.Y.Z Succeeded

# Check the Operator's Deployment
oc get deploy -n openshift-operators | grep node-health-check-operator-controller-manager
# Wait for 1/1 READY
```

## Configure the NHC

!!!(nhc-configuration.yaml)!!!

Create the config

```
oc create -f my-worker-nhc.yaml
```

## Verify the configuration

```
oc get nodehealthcheck nhc-worker-default
```
