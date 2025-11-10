# Create an extra network line with VLAN trunking to support 2 VLANs

**Note that we configure always the NNCP in a way that we have multiple bridge-mappings but only a single bridge**

## Create the NNCP for cluster wide additional networks using VLANs

The NNCP contains a single bridge that is (here) using a single network interface (only - in production, this should rather be a bond).
The NNCP configures only the bridge with the VLANs to use later on. However, in order to consume it for different NADs, one needs to confiure multiple bridge-mappings. Those are configured as a list. One might prepare multiple of those mappings for future assignment to different NADs without reconfighuring the NNCP, especially if many NADs are expected to be configured on the go while many NADs are already in place.

Further on, different NADs will use then unique bridge mappings.

```
!!!include(vm-networks-2-VLANs-nncp.yaml)!!!
```

## Create the NADs cluster wide with distinct VLANs per network - for outside access configuration

NADs for the different namespaces will be configured using the bridge mappings defined above.
The `name` and `namespace` names used in the `metadata` for the NAD object must match the configurationg applied: `netAttachDefName` must be of structure `<namespace>/<nad_name>`:

In the above example, both NADs are provided to the `default` namespace in order to allow all namespaces to use those networks.

## Alternative: Create the NNCP for namespace specific additional networks using VLANs

Alternatively, if the NADs should be available only to specific namespaces, each namespace must use it's own defintion of the NAD using the smae definitions.

```
!!!include(vm-networks-2-VLANs-nads-defauilt.yaml)!!!
```

Since the NADs should be available only to specific namespaces, each namespace must use it's own defintion of the NAD using the smae definitions. In turn, more bridge-mappings must be configured for the NNCP:

## Alternative: Create the NADs for only selected namespaces with distinct VLANs per network - for outside access configuration

## **VALIDATE VALIDATE VALIDATE VALIDATE VALIDATE VALIDATE**

```
!!!include(vm-networks-2-VLANs-nncp-separateprojects.yaml)!!!
```

With this enhanced set of available bridge-mappings, a specific configuration per namespace can be provided, however, each NAD per namespace per network to configure. However, a fine granular networking confiugration can be created (micro-segmentation and micro-configuration).

```
!!!include(vm-networks-2-VLANs-nads-separateprojects.yaml)!!!
```
