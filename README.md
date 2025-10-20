# openshift-virt-pocs

# Networking

## local networks without access from / to outside - but no pod communication using the default network

Execept telemetry and health checks (those are always going through the default network unless shut down)

### local network for smaller subnets within a namespace

For smaller subnets, layer2 networks can be used, spanning multiple nodes.

### local networks for large subnets within a namespace

For larger subnets, it's good keeping local traffic for subnet within the node. All remote node traffic will be routed into another subnet.
[Is a VM migrated to another node then in another subnet ?]

### local networks for large subnets across namespaces

Using CUDN for layer 3 .....

## local networks with access from /to outside (localnet)

### local network for smaller subnets

Using UDN layer2 on localnet with access to/from other external network.

### local networks for small subnets connecting different namespaces

Using CUDN laayer2 on localnet with access to/from other external network.

### local networks for large subnets

Using UDN layer3 on localnet with access to/from other external network. Is this possible without BGP ?

### local networks for large subnets connecting different namespaces

Using CUDN layer3 on localnet with access to/from other external network. Is this possible without BGP ?

## local networks with VLANs (external access)

### The example of using different VLANs across external network.

### The example of using different VLANs for primary network to isolate fully pod network traffic (also to API) from each other

### The example for all above when having external network already using VLANs for host network.

## BGP advertised UDNs

# Compute

## VM classes

## templates

## VM creation pipeline

## Descheduler

### deschdeluer rules

## VM placement and separation

## cluster quota for 50% headroom per site in 2 main DC

# Storage

## Storage allocation

## Snapshots and Cloning

## Storage Live Migration

##

# Automation
