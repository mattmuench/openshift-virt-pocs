# Shared network interface for live migration as well as for mounting NFS to the hosts for PVs - using the same VLAN

In this scenario, the hosts have a host/pod network interface and only an additional interface that should be shared for

- accessing the NFS shares for creating PVs with low traffic
- having a dedicated network for live migration
  All parties using the network connection are required to use a specific VLAN tag and an IP address from the same subnet through DHCP.

There are two different access points to configure, however, using the same VLAN tag and IP addresses from the same subnet, resulting in two different interfaces to attach to the same physical interface:

- a host level interface to be used by the host for mounting eventually an NFS share
- a localnet interface for providing the network to the network attachment definition to the virtualization live migration

## Parts of the configuration - NAD based configuration of network access for live migration

Since the live migration network would be provided to the virtualization through an NAD, a localnet configuration is needed to attach to the extra NIC.
Because it's required to use VLAN tagging on the connection, the NAD uses a VLAN tag.

DHCP is configured, but because the live migration would pick it's own IP addresses on the fly from the NAD's range of the subnet, one needs to make sure to reserve a range for this purpose being wide enough to facilitate more parallel migrations with multiple hosts. In real environments, it's better to reserve a private (unused) network with a range being wide enough.

Note that in this specific configuration here, the network range picked from the shared subnet is very limited.

```
!!!include(localnet-live-migration-nad-vlan-subnet.yaml)!!!
```

## Parts of the configuration - base network interface configuration for host access and localnet

The localnet configuration for the NAD must be done through a ovs-bridge. In order to avoid directly configuring the inetrface with an addition VLAN tagged one, the configuration for the host access would use an attachment to the ovs-bridge that is configured for the NAD from above.

The configuration is two-fold:

- an ovs-bridge for all communicaiton through the physical interface
- two ports for internal attachment, being one for the localnet in an untagged way and one for the host access being tagged

This allows to reuse the configuration with additional localnets as well as additional host network communication lines a the similar way.

```
!!!include(shared-network-for-host-and-pods-using-vlans.yaml)!!!
```

## Resulting configuration

Since no specific mac addresses had been specified and no mac address propagation is configured for the ports, the host level new interface is getting a new mac address assigned automatically.

Because mounting an NFS share doesn't require a stable IP address, going with DHCP based assignment should work here.

## Pitfalls and alternatives

Because of the DHCP based assignment, the network range must be configured properly to allow the different use cases to not overlap. Since the MAC addresses could change, it would be better to assign a static unique MAC address. Note that this configuration would require individual NNCPs per node to configure.

```
!!!include(shared-network-for-host-and-pods-using-vlans-staticmac.yaml)!!!
```
