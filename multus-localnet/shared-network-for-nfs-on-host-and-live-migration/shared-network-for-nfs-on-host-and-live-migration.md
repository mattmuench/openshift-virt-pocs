# Shared network interface for live migration as well as for mounting NFS to the hosts for PVs - using the same VLAN

In this scenario, the hosts have a host/pod network interface and only an additional interface that should be shared for

- accessing the NFS shares for creating PVs with low traffic
- having a dedicated network for live migration

All parties using the network connection are required to use a specific VLAN tag and an IP address from the same subnet using DHCP.

There are two different access points to configure, resulting in two different interfaces to attach to the same physical interface:

- a host level interface to be used by the host for mounting eventually an NFS share
- a localnet interface for providing the network through a network attachment definition to the virtualization live migration

## NAD based configuration of network access for live migration

The live migration network would be provided to the virtualization through an NAD and a localnet configuration is needed to attach to the extra NIC.
Because it's required to use VLAN tagging on the connection, the NAD uses a VLAN tag.

DHCP is configured, but because the live migration would pick it's own IP addresses on the fly from the NAD's range of the subnet, one needs to make sure to reserve a range for this purpose being wide enough to facilitate more parallel migrations with multiple hosts. In real environments, it's better to reserve a private (unused) network with a range being wide enough.

Note that in this example configuration here, the network range picked from the shared subnet is very limited.

```
!!!include(localnet-live-migration-nad-vlan-subnet.yaml)!!!
```

## Recommended - Option 1: Base network interface configuration for host access and localnet - using a direct VLAN interface

The localnet configuration for the NAD must be done through a ovs-bridge. However, for the host access to the NFS share, an additional vlan interface to the base host interface would be sufficient.

In addition, the IP address asignment is easier to align with the outside world, because the mac address of the base interface could be used to assign a known IP address through DHCP.

The configuration has three elements:

- on additional VLAN interface on the physical interface
- an ovs-bridge for all communication through the physical interface
- a port for the internal attachment for the localnet in an untagged way

```
!!!include(shared-network-for-host-and-pods-using-vlans-staticmac.yaml)!!!
```

## Option 2: Base network interface configuration for host access and localnet - using a bridge port

The localnet configuration for the NAD must be done through a ovs-bridge. In order to avoid directly configuring the interface with an addition VLAN tagged one, the configuration for the host access would use an attachment to the ovs-bridge that is configured for the NAD from above.

The configuration is two-fold:

- an ovs-bridge for all communicaiton through the physical interface
- two ports for internal attachment, being one for the localnet in an untagged way and one for the host access being tagged

This allows to reuse the configuration with additional localnets as well as additional host network communication lines a the similar way.

```
!!!include(shared-network-for-host-and-pods-using-vlans.yaml)!!!
```

## Apply the configuration

Create the NNCP configuration file as desired per option 1 or option 2. In the below example, `shared-network-for-host-and-pods-using-vlans.yaml` is used.

Apply the configuration and wait for the networkNodeConfigurationPolicy to become `Available`:

```
[username@nodename ]$ oc create -f shared-network-for-host-and-pods-using-vlans.yaml
nodenetworkconfigurationpolicy.nmstate.io/live-migration-shared created
[username@nodename ]$ oc get nncp
NAME                           STATUS      REASON
...
live-migration-shared          Available   SuccessfullyConfigured
...
[username@nodename ]$
```

Create the NAD configuraiton file from above. In the exmaple below, `localnet-live-migration-nad-vlan-subnet.yaml` is used.  
Then apply the NAD for the live migration network for OpenShfit Virtualization and check for its existance:

```
[username@nodename ]$ oc apply -f localnet-live-migration-nad-vlan-subnet.yaml
networkattachmentdefinition.k8s.cni.cncf.io/nad-lm created
[username@nodename ]$ oc -n openshift-cnv get network-attachment-definition
NAME     AGE
nad-lm   36s
[username@nodename ]$
```

## Resulting configuration - option 1

The live migration network, assigned to virtualization live migration (and the hyperconverged-kubevirt instance), uses a subnet through the NAD from a range of 192.168.22.224/29 and VLAN 3876.
The nodes are able to access an NFS server living on the subnet 192.168.22.64/26 using VLAN 3876. The node's IP addresses are assigned permanently through DHCP.

## Resulting configuration and possible pitfalls - option 2

It provides the same basic functionality as required as option 1. However, while it's more flexible for transparently scaling it, it has some potential for challenges.

Since no specific mac addresses were specified, the host level new interface is getting a new mac address assigned automatically.

Mounting an NFS share doesn't require a stable IP address and going with DHCP based assignment could work here - if there is no requirement to dynamically assign IP addresses reliably.

Because of the DHCP based assignment, the network range must be configured properly to allow the different use cases to not overlap.
