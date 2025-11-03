# Installation and configuration of the Self Node Remediation Operator

## Installing the operator

(Note sure what really works fro the subscription => choose to use the console based installation and then configure it)
**Create a namespace for the operator**

```
!!!include(snro-namespace.yaml)!!!
```

Apply the namespace definition.

```
[root@ocp68-jump snro-install]# oc apply -f snro-namespace.yaml
namespace/openshift-workload-availability created
[root@ocp68-jump snro-install]#
```

**Create the operator group**

```
!!!include(snro-operatorgroup.yaml)!!!
```

Apply the operator group definition.

```
[root@ocp68-jump snro-install]# oc apply -f snro-operatorgroup.yaml
operatorgroup.operators.coreos.com/workload-availability-operator-group created
[root@ocp68-jump snro-install]# cat snro-operatorgroup.yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: workload-availability-operator-group
  namespace: openshift-operators
[root@ocp68-jump snro-install]#
```

**Create subscription for the operator**

Note that the approval strategy is set to Manual. It's recommended to aply this to understand when the operator is degraded because of any issues and no to mix up with an update. Because the update should be performed only through maintenance windows to avoid putting production SLA at risk, automatic should be rather applied for test environments.

```
!!!include(snro-subscription.yaml)!!!
```

Apply the subscription and wait for the status to become Available.

```
[root@ocp68-jump snro-install]# oc apply -f snro-subscription.yaml
subscription.operators.coreos.com/self-node-remediation-operator created
[root@ocp68-jump snro-install]#
[root@ocp68-jump snro-install]# oc get installplan
NAME            CSV                             APPROVAL   APPROVED
install-jdb8t   self-node-remediation.v0.10.2   Manual     true
[root@ocp68-jump snro-install]#
...
...
...

[root@ocp68-jump snro-install]# oc get pods -o wide
NAME                                                        READY   STATUS    RESTARTS        AGE     IP             NODE      NOMINATED NODE   READINESS GATES
self-node-remediation-controller-manager-6846c9f787-l76tv   2/2     Running   1 (3m52s ago)   4m4s    10.129.0.80    master3   <none>           <none>
self-node-remediation-ds-5rjqx                              1/1     Running   1 (3m20s ago)   3m23s   10.129.0.81    master3   <none>           <none>
self-node-remediation-ds-gvx2c                              1/1     Running   1 (3m20s ago)   3m23s   10.128.0.216   master2   <none>           <none>
self-node-remediation-ds-z9jc5                              1/1     Running   1 (3m20s ago)   3m23s   10.130.1.37    master1   <none>           <none>
[root@ocp68-jump snro-install]#
[root@ocp68-jump snro-install]# oc get ds
NAME                       DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
self-node-remediation-ds   3         3         3       3            3           <none>          27m
[root@ocp68-jump snro-install]#
```

## Configure the SNRO

(Defaults may work but need to be investigated according to the envrionment.)

Create the config file and create the config (refer to individual settings in [link](https://docs.redhat.com/en/documentation/workload_availability_for_red_hat_openshift/25.8/html/remediation_fencing_and_maintenance/self-node-remediation-operator-remediate-nodes#understanding-self-node-remediation-operator-config_self-node-remediation-operator-remediate-nodes) )

Note: In the example below, a custom DaemonSet tolaration is configured, however, in the node the label is not set.

```
!!!include(snro-config.yaml)!!!
```

```
[root@ocp68-jump snro-install]# oc create -f snro-config.yaml
selfnoderemediationconfig.self-node-remediation.medik8s.io/self-node-remediation-config configured
[root@ocp68-jump snro-install]# oc get selfnoderemediationconfigs
NAME                           AGE
self-node-remediation-config   17m
[root@ocp68-jump snro-install]#
```

Check the setting for the applied startegy and correct accordingly. In the actual default configuration applied, the `remediationStrategy` is set to `Automatic` which is the default.

```
[root@ocp68-jump snro-install]# oc get selfnoderemediationtemplate
NAME                                                AGE
self-node-remediation-automatic-strategy-template   28m
[root@ocp68-jump snro-install]# oc get selfnoderemediationtemplate/self-node-remediation-automatic-strategy-template -o yaml
apiVersion: self-node-remediation.medik8s.io/v1alpha1
kind: SelfNodeRemediationTemplate
metadata:
  annotations:
    remediation.medik8s.io/multiple-templates-support: "true"
  creationTimestamp: "2025-10-29T15:33:26Z"
  generation: 1
  labels:
    remediation.medik8s.io/default-template: "true"
  name: self-node-remediation-automatic-strategy-template
  namespace: openshift-workload-availability
  resourceVersion: "113743156"
  uid: f01b7983-f777-407c-8604-7a0902ee348a
spec:
  template:
    spec:
      remediationStrategy: Automatic
[root@ocp68-jump snro-install]#
```
