# Node Health Check operator installation and configuration using the CLI

**Important: in order to use any remediation techniques, the NHC operator must be installed.**

## Install the operator

One doesn't ned to create a new namespace since the operator goes to openshift-operators that should be there anyways.

```
# nhc-operator-group.yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: openshift-nhc-operatorgroup
  namespace: openshift-operators
spec:
  # The targetNamespaces field is often omitted for cluster-scope operators, 
  # or set to the installation namespace.
  targetNamespaces:
  - openshift-operators
```

Create the operator group.

```
oc create -f nhc-operatorgroup.yaml
```

Create a a subscription.

```
# nhc-subscription.yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: node-healthcheck-operator
  namespace: openshift-operators
spec:
  channel: stable # Specify your preferred channel (e.g., stable, fast)
  installPlanApproval: Automatic # Set to Manual if you want to inspect InstallPlan before deployment
  name: node-healthcheck-operator
  source: redhat-operators # Or 'community-operators' if using the community version
  sourceNamespace: openshift-marketplace
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
