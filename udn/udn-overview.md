### Creating local private networks - namespace specific

Local network resources can be created as cluster wide or namespace scoped resources. The resource name for those local networks in Openshift is User Defined Networks (NAD).

**Scope of local networks**\
Cluster wide NAD resources can be consumed by any VM administrator for providing connectivity between VMs across namespaces.
Namespace scoped NAD can be used to connect VMs across selected namespaces exclusively.

**Kinds of local networks**\
Local networks can be created as layer 2 or layer 3 networks.

Cluster scoped UDNs are created on the default namespace.

In order to create namespace scoped UDNs, those namespaces must have been created using a `k8s.ovn.org/primary-user-defined-network` label. In adition, the UDN definition must mention the namespaces that it should be only available to.

**Avoiding overlapping**\
Since the UDN traffic is encapsulated anyways when travelling over the cluster and host network, there shouldn't be any clashes.

However, regarding the cluster network, there should be no overlapping of the ranges with the UDN. The default network will still be connected to the pod for metrics purposes, at least, and an overlapping might produce unpredictable routing for the VM traffic.

With regards to other UDNs configured, there should be - naturally - no overlapping at all within the same VM. UDNs configured for other namespaces might use the same chosen CIDR without any issues.

With regards to perhaps cluster UDNs, overlapping of CIDRs must be avoided too. If an admin is allowed to create namespaced UDNs, one should check for possible cluster UDNs configured for the affected namespaces.

**Use of pod network**
Even with those new primary networks, where the pod/VM communications happens not using the default pod network anymore but the newly created specific network, the pod network would not be removed and is available as an infrastructure network. It would be used to gather metrics and logs from the VM and might help for integration with the guest OS through the guest tools.

**Applying the primary network to a VM**
The primary network is made available through the namespace definition directly by specifying 'default' as the network name. This way, independent of the actual namespace and effective primary network name, any VM will be properly connected to the default network.
