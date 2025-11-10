# Installation and configuration of the Fence Agents Remediation operator

## Preparation of the namespace

If the namespace `openshift-workload-availability` is not created yet (and no SNRO or MDR is installed and confiured), create the namespace and create an operator group:

Create a namespace definition file and apply it (create the namespace):

```
!!!include(far-namespace.yaml)!!!
```

```
oc apply -f far-namespace.yaml
```

Create an operator group defintion file and apply it:

```
!!!include(far-operatorgroup.yaml)!!!
```

```
oc apply -f far-operatorgroup.yaml
```

## Create a subscription

Create a subscription definition file and create the subscription:

```
!!!include(far-subscription.yaml)!!!
```

```
[root@ocp68-jump far-install]# oc create -f far-subcription.yaml
subscription.operators.coreos.com/fence-agents-remediation-subscription created
[root@ocp68-jump far-install]#
[root@ocp68-jump far-install]# oc get sub
NAME                                    PACKAGE                    SOURCE             CHANNEL
fence-agents-remediation-subscription   fence-agents-remediation   redhat-operators   stable
self-node-remediation                   self-node-remediation      redhat-operators   stable
[root@ocp68-jump far-install]#
```

In the above example output, the Self Node Remediation operator was already installed and hence the subscription is listed here too.

Check for the installation of the operator:

```
[root@ocp68-jump far-install]# oc get deployment
NAME                                       READY   UP-TO-DATE   AVAILABLE   AGE
self-node-remediation-controller-manager   1/1     1            1           103m
[root@ocp68-jump far-install]#
[root@ocp68-jump far-install]# oc get pods
NAME                                                        READY   STATUS        RESTARTS       AGE
self-node-remediation-controller-manager-6846c9f787-l76tv   2/2     Terminating   1 (105m ago)   105m
self-node-remediation-controller-manager-6846c9f787-tcdkl   2/2     Running       1 (17m ago)    18m
self-node-remediation-ds-5rjqx                              1/1     Running       1 (105m ago)   105m
self-node-remediation-ds-gvx2c                              1/1     Running       1 (105m ago)   105m
self-node-remediation-ds-z9jc5                              1/1     Running       1 (105m ago)   105m
[root@ocp68-jump far-install]#
```

There is no deployment yet and no operator pods. Check the subscription success:

```
[root@ocp68-jump far-install]# oc describe sub/fence-agents-remediation-subscription
Name:         fence-agents-remediation-subscription
Namespace:    openshift-workload-availability
Labels:       operators.coreos.com/fence-agents-remediation.openshift-workload-availability=
Annotations:  <none>
API Version:  operators.coreos.com/v1alpha1
Kind:         Subscription
Metadata:
  Creation Timestamp:  2025-10-29T17:13:50Z
  Generation:          1
  Resource Version:    113831352
  UID:                 1f686fe3-1342-4c8d-aa82-255349bd2c24
Spec:
  Channel:           stable
  Name:              fence-agents-remediation
  Source:            redhat-operators
  Source Namespace:  openshift-marketplace
Status:
  Current CSV:              fence-agents-remediation.v0.6.0
  Install Plan Generation:  2
  Install Plan Ref:
    API Version:       operators.coreos.com/v1alpha1
    Kind:              InstallPlan
    Name:              install-pmp57
    Namespace:         openshift-workload-availability
    Resource Version:  113830323
    UID:               79623bf6-f149-469b-ac23-cf37d032e060
  Installplan:
    API Version:  operators.coreos.com/v1alpha1
    Kind:         InstallPlan
    Name:         install-pmp57
    Uuid:         79623bf6-f149-469b-ac23-cf37d032e060
  Last Updated:   2025-10-29T17:17:12Z
  State:          UpgradePending
Events:           <none>
[root@ocp68-jump far-install]#
```

If the previous operator was installed using the manual approval for updates, all other operators in the same namspace use it too, independent on what was configured for the new operator added. In this case, the install plan must be approaved manualy.

```
[root@ocp68-jump far-install]# oc get installplan
NAME            CSV                               APPROVAL   APPROVED
install-jdb8t   self-node-remediation.v0.10.2     Manual     true
install-pmp57   fence-agents-remediation.v0.6.0   Manual     false
[root@ocp68-jump far-install]#
[root@ocp68-jump far-install]# oc patch installplan install-pmp57 --namespace openshift-workload-availability --type merge --patch '{"spec":{"approved":true}}'
installplan.operators.coreos.com/install-pmp57 patched
[root@ocp68-jump far-install]#
[root@ocp68-jump far-install]# oc get installplan
NAME            CSV                               APPROVAL   APPROVED
install-jdb8t   self-node-remediation.v0.10.2     Manual     true
install-pmp57   fence-agents-remediation.v0.6.0   Manual     true
[root@ocp68-jump far-install]#
[root@ocp68-jump far-install]# oc get pods,deployment
NAME                                                               READY   STATUS        RESTARTS       AGE
pod/fence-agents-remediation-controller-manager-7f655464f9-nwq64   2/2     Running       0              58s
pod/fence-agents-remediation-controller-manager-7f655464f9-zzp74   2/2     Running       0              58s
pod/self-node-remediation-controller-manager-6846c9f787-l76tv      2/2     Terminating   1 (111m ago)   111m
pod/self-node-remediation-controller-manager-6846c9f787-tcdkl      2/2     Running       1 (23m ago)    23m
pod/self-node-remediation-ds-5rjqx                                 1/1     Running       1 (110m ago)   110m
pod/self-node-remediation-ds-gvx2c                                 1/1     Running       1 (110m ago)   110m
pod/self-node-remediation-ds-z9jc5                                 1/1     Running       1 (110m ago)   110m

NAME                                                          READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/fence-agents-remediation-controller-manager   2/2     2            2           58s
deployment.apps/self-node-remediation-controller-manager      1/1     1            1           111m
[root@ocp68-jump far-install]#
```

## Configure the FAR with the appropriate parameters

See [link](https://docs.redhat.com/en/documentation/workload_availability_for_red_hat_openshift/25.8/html/remediation_fencing_and_maintenance/fence-agents-remediation-operator-remediate-nodes#supported-agents-fence-agents-remediation-operator_fence-agents-remediation-operator-remediate-nodes) for supported FAR agents.

An example configuration for an IPMI configuration is below in far-agent.yaml:
Consider that all BMC IP DNS names follow the node names of a name template of ${nodename}-bmc-ip.
Note that `remediationStrategy: OutOfServiceTaint` should be used in all cases that are not in the cloud and are not bare metal IPI.

```
!!!include(far-agent.yaml)!!!
```

## Create node specific secrets

Create for each of the nodes a base64 encoded string with the password for the IPMI login of a server - per node: (Watch the passwords and nodenames !)

```
[root@ocp68-jump far-install]# echo -n 'MyW1r3dPa55w0rd' | base64
TXlXMXIzZFBhNTV3MHJk
[root@ocp68-jump far-install]#
```

Create a secret defintion file:

```
apiVersion: v1
kind: Secret
metadata:
  # The Secret name must match the templated name: {{ .Name }}-bmc-secret -- from the above section for
  name: worker-01-bmc-secret
  namespace: openshift-workload-availability
type: Opaque
data:
  # The key 'password' is matched to the 'name' field in your nodeSecretNames:
  # The value is the Base64 encoded password from Step 1.
  password: TXlXMXIzZFBhNTV3MHJk
```

```
[root@ocp68-jump far-install]# oc create -f master1-bmc-secret.yaml
secret/master1-bmc-secret created
[root@ocp68-jump far-install]#
```

## Create node specific configuration for Redfish

For getting the systems UUID, execute towards the Redfish access point:
`curl -k -u [username]:[password] https://<CIMC_IP_Address>/redfish/v1/Systems`
One can find it in the URI in @odata.id value.

In Cisco UCS web interface, access the CIMC web interface, switch to the server overview and check there for UUID or System UUID.
