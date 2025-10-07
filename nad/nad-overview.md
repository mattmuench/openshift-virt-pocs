### Creating local private networks - namespace specific

Local network resources can be created as cluster wide or namespace scoped resources. The resource name for those local networks in Openshift is User Defined Networks (NAD).

**Scope of local networks**
Cluster wide NAD resources can be consumed by any VM administrator for providing connectivity between VMs across namespaces.
Namespace scoped NAD can be used to connect VMs across selected namespaces exclusively.

**Kinds of local networks**
Local networks can be created as layer 2 or layer 3 networks.

Cluster scoped UDNs are created on the default namespace.

In order to create namespace scoped UDNs, those namespaces must have been created using a `k8s.ovn.org/primary-user-defined-network` label. In adition, the UDN definition must mention the namespaces that it should be only available to.
