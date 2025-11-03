# Creating local private networks - namespace specific - using the console

An overview is available in [Overview to local networks](nad-overview.md).

Namespace specific NADs can be used to provide an isolated local network that is not using the pod subnet. This is useful if an administrator needs to isolate any communication between pods or VMs from any other network and the potential access from unauthorized resources.

**Note:**
"Currently, creation of a UserDefinedNetwork CR with a Layer3 topology or a Secondary role are not supported when using the OpenShift Container Platform web console." [link](https://docs.redhat.com/es/documentation/openshift_container_platform/4.19/html-single/multiple_networks/index#nw-udn-cr-ui_about-user-defined-networks)

**Note:**
"You must consider the following limitations before implementing a primary UDN:

You cannot use the virtctl ssh command to configure SSH access to a VM.
You cannot use the oc port-forward command to forward ports to a VM.
You cannot use headless services to access a VM.
You cannot define readiness and liveness probes to configure VM health checks." [link](https://docs.redhat.com/es/documentation/openshift_container_platform/4.19/html-single/virtualization/index#virt-connecting-vm-to-primary-udn)

## 1. Create new namesapces configured for the use with UDNs

Using the main menu, create a namespace but directly during creation, specify the label `k8s.ovn.org/primary-user-defined-network`.

![UI use to create a namespace - main menu](images/create-namespace-menu.png)

![UI: create first namespace with the specific label applied:](images/create-namespace-nad.png)

![UI: create second namespace with the specific label applied:](images/create-namespace-nad2.png)

## 2. Inform yourself about networks in use with the individual hypervisor cluster

Prepare for creating a UDN with a specific CIDR. The IP addresses for the VMs in primary UDNs with a layer 2 topology are provided automatically. A VM would need to use DHCP to configure the network interface in order to be able to use the layer 2 network properly. Those assigned IP addresses will be retained automatically to avoid handing out the same IP address to different instance upon reboot or migrating VMs.

In order to avoid clashes with cluster networks in use, one would check the cluster IP address ranges in use before selecting the CIDR to use. One can check it from the console. If one has no access to the cluster config, check with the administrator of the cluster which network settings are safe to be used in UDNs.

Select _Administration_ and _CustomResourceDefinitions_ and then type in the search field _networks.config_ . Only one item is listed marked with _CRD_ named _network_. Then switch the submenu in the window to _Instances_, select the link for the entry _NO_ _cluster_ and then switch the submenu of the newly displayed page to _YAML_ view.\
![UI view of OpenShift console to create UDNs](images/udn-user-check-cluster-networks.png)
![UI view of OpenShift console to create UDNs](images/udn-user-check-cluster-networks-config.png)
![UI view of OpenShift console to create UDNs](images/udn-user-check-cluster-networks-config-instance.png)
![UI view of OpenShift console to create UDNs](images/udn-user-check-cluster-networks-config-instance-yaml.png)

The used network ranges by the cluster are listed there, once the user scrolls down to the _spec:_ section. In the above screenshot, the used networks are the one for _clusterNetwork_ being `10.128.0.0/14` and the _serviceNetwork_ being `172.30.0.0./16`. These settings are configured during cluster installation and are specific to the individual configuration.

Once completed, close the view with _Cancel_.

## 3. Create the UDN

One must create a network resource to consume it with VMs (and pods).

**Note:** Up to OpenShift version 4.19, the local network resource must be created upfront. Later versions of OpenShift might allow an on-the-fly creation of the network resource at the time of a VM creation.

From the main menu under _Networking_, select _UserDefinedNetworks_. Then select Create and from the dropdown menu the _UserDefinedNetwork_.\
![UI view of OpenShift console to create UDNs](images/udn-main-menu.png)

![UI view of OpenShift console to create UDNs](images/udn-new-user-udn.png)

![UI view of OpenShift console to create UDNs](images/udn-user-udn-starting.png)\

This view provides initially the blank fields that a user must provide. However, the _Project name_ provides a list of namespaces that have the above label applied. A namespace scoped UDN must provide a project name that this UDN will be provided for.

![UI view of OpenShift console to create UDNs](images/udn-user-udn-selection.png)\

Select the CIDR to use inside the layer 2 network. The IP addresses for the VMs are provided automatically. A VM would need to use DHCP to configure the network interface in order to be able to use the layer 2 network properly. Those assigned IP addresses will be retained automatically to avoid handing out the same IP address to different instance upon reboot or migrating VMs.

Finally, select _Create_ to the the UDN.\

![UI view of OpenShift console to create UDNs](images/udn-user-udn-specification.png)\
![UI view of OpenShift console to create UDNs](images/udn-user-udn-created.png)\

In the listing, one may find the IP address range assigned as well as the namespace it was configured. Note that this UDN is only visible in the namespace selected

Once a namespace scoped UDN is configured, automatically it's provided to the namespace through a Network Attachment Definiiton (NAD). This can be seen when going to the main menu and from thre to _Networking_ and _NetworkAttachmentDefinitions_. If the right hand side displays another project name than the selected one, perhaps no NAD is displayed. With the right project selected the NAD is shown as a "primary-udn" entry.\

![UI view of OpenShift console to create UDNs](images/udn-user-udn-created-nad.png)\

**Note:** Only one primary UDN can be created in any namespace. If a user wanted to use additional networks, secondary networks must have been created and provisioned in addition.

## 4. Create VMs using the new local network

Create two VMs using the same namespace but the new local network resource, the UDN, for communication. This is done automatically for the VMs inside this namespace and doesn't require additional configuration, at least from network config side. In the example below, the VM name is changed to rhel8-vm2 only.\

![UI view of OpenShift console to create UDNs](images/udn-user-udn-vm2-create.png)\

Already from the overview of the started VM, the assigned IP address is listed.\
![UI view of OpenShift console to create UDNs](images/udn-user-udn-vm2-running-network-address.png)\

## Then start the VM, login to the console, and check the network address assigned to the VM network.

The peer VM inside the same namespace should be able to ping the peer VM:\
![UI view of OpenShift console to create UDNs](images/udn-user-udn-vm1-to-vm2-ping.png)\

# NO - PARKING LOT for other use case:

In the VM specification, select _Customize_ and then activate the _Network interfaces_ submenu. A default network interface is available. If full isolation is to be achieved and no transparent network access to extern is allowed, one can switch it off or deleet it fully from the config menu.\

![UI view of OpenShift console to create UDNs](images/udn-user-udn-vm1-create-custom-network.png)\

In order to use the new interface, however, through _Add network interface_ one may create an additional network interface.

The VM should come up and the network interface should list a valid IP address for the configured UDN range.

====== wrong
This is a doc bug:\
![UI view of OpenShift console to create UDNs](images/BUG-primary-udn-config-of-a-vm.png)\
==> It's just wrong to change the name in 4.19.

My text:

Since one cannot create a VM using the primary UDN as the network interface fully through the UI, an initial base version of the - although beside networking - fully configured VM must be created without starting it. This is by deselecting the _Start this VirtualMachine after creation (Always)_ which will turn then into _Start this VirtualMachine after creation (Halted)_. The finish creation of the VM and wait for the VM being provisioned and stopped.\

![UI view of OpenShift console to create UDNs](images/udn-user-udn-vm1-prepare-vm-base.png)\

After the VM is created but stopped, switch from the _Overview_ submenu to the _YAML_ submenu and scroll down until the `devices:` section in the `spec.template.spec.domain` defintions:\
![UI view of OpenShift console to create UDNs](images/udn-user-udn-vm1-change-vm-base-to-udn-yaml.png)\

There, change in the section of `interfaces:` the name of the binding to `primary-udn` and in the section of `networks:` the name to `primary-udn` too.

```
interfaces:
  - binding:
      name: l2bridge
    model: virtio
    name: primary-udn
    ...
networks:
  - name: primary-udn
    pod: {}
```

to end up with this section as shown below:\
![UI view of OpenShift console to create UDNs](images/udn-user-udn-vm1-change-vm-base-to-udn-changed-yaml.png)\

Repeat the same steps to create a second VM inside the same namespace.
