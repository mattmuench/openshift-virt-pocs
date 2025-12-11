# Creating localnets across nodes with different NICs

The difference is here that without a node selector, the NNCP will be applied to all nodes.

To select a configuration for individual node(s), a nodeSelector is set.

The localnet's names must be, however, identical across the nodes even those must use different physical NICs.

```
!!!include(vm-networks-extranet-different-nics.yaml)!!!
```
