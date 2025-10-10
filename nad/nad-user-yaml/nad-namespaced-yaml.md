# Creating local private networks - namespace specific - using the CLI

Goal: As an administrator, I want to create private networks within a namespace that VMs can communicate on without the need of an additional network and no external access. I want to use the CLI only.

An overview is available in [Overview to local networks](nad-overview.md).

Namespace specific NADs can be used to provide an isolated local network that is not using the pod subnet. This is useful if an administrator needs to isolate any communication between pods or VMs from any other network and the potential access from unauthorized resources.

**Note:**
"Currently, creation of a UserDefinedNetwork CR with a Layer3 topology or a Secondary role are not supported when using the OpenShift Container Platform web console." [link](https://docs.redhat.com/es/documentation/openshift_container_platform/4.19/html-single/multiple_networks/index#nw-udn-cr-ui_about-user-defined-networks)

**Note:**
"You must consider the following limitations before implementing a primary UDN [link](https://docs.redhat.com/es/documentation/openshift_container_platform/4.19/html-single/virtualization/index#virt-connecting-vm-to-primary-udn):

- You cannot use the virtctl ssh command to configure SSH access to a VM.
- You cannot use the oc port-forward command to forward ports to a VM.
- You cannot use headless services to access a VM.
- You cannot define readiness and liveness probes to configure VM health checks."

**Prerequisite:**
The station of choice running the CLI should have been installed the virtctl CLI. This will be used to connect to the VM later for checking the communication between VMs over the local private network.

## 1. Create new namespaces configured for the use with UDNs

Example namespace defintion is created here in the file `nad-namespace-namespace-with-nad.yaml`

```
!!!include(nad-namespace-namespace-with-nad.yaml)!!!
```

Create the new namespace.

```
oc create -f nad-namespace-namespace-with-nad.yaml
```

## 2. Optional: Inform yourself about networks in use with the individual hypervisor cluster

Since the UDN traffic is encapsulated anyways when travelling over the cluster and host network, there shouldn't be any clashes. However, using different CIDRs might ease any troubleshooting when not having overlapping use of CIDRs in different layers of the network.

Prepare for creating a UDN with a specific CIDR. The IP addresses for the VMs in primary UDNs with a layer 2 topology are provided automatically. A VM would need to use DHCP to configure the network interface in order to be able to use the layer 2 network properly. Those assigned IP addresses will be retained automatically to avoid handing out the same IP address to different instance upon reboot or migrating VMs.

In order to avoid potential clashes with cluster networks in use, one would check the cluster IP address ranges in use before selecting the CIDR to use. One can check it from the console. If one has no access to the cluster config, check with the administrator of the cluster which network settings are safe to be used in UDNs.

Example:

```
[root@acm41-jump ~]# oc get -o yaml networks.config.openshift.io cluster
apiVersion: config.openshift.io/v1
kind: Network
metadata:
  name: cluster
  ...
spec:
  clusterNetwork:
  - cidr: 10.128.0.0/14
    hostPrefix: 23
  externalIP:
    policy: {}
  ...
  networkType: OVNKubernetes
  serviceNetwork:
  - 172.30.0.0/16
status:
...
[root@acm41-jump ~]#
```

In the above example, the used networks are the one for _clusterNetwork_ being `10.128.0.0/14` and the _serviceNetwork_ being `172.30.0.0./16`. These settings are configured during cluster installation and are specific to the individual configuration.

## 3. Create the UDN

One must create a network resource to consume it with VMs (and pods). Layer 2 UDNs assign an IP address from a range specified automatically for the VMs. TO retain the IP address of the VM throughout the lifecycle pf the VM, the `ipam.lifecycle` setting should be set to `persistent`. Without this setting, the IP address could be reassigned to any other pod or VM upon restart or during live migration to another node.

**Note:** Up to OpenShift version 4.19, the local network resource must be created upfront. Later versions of OpenShift might allow an on-the-fly creation of the network resource at the time of a VM creation.

A VM would need to use DHCP to configure the network interface in order to be able to use the layer 2 network properly. Those assigned IP addresses will be retained automatically when configured.

Create a file for the UDN configuration, like here in the file `nad-namespaced-udn.yaml`:

```
!!!include(nad-namespaced-udn.yaml)!!!
```

Create the new udn resource.

```
oc create -f nad-namespaced-udn.yaml
```

Check the resource is being created.

```
[root@acm41-jump ns-4]# oc get -n namespace-4 userdefinednetwork
NAME             AGE
udn-primary-l2   35s
[root@acm41-jump ns-4]#
```

Once a namespace scoped UDN is configured, automatically it's provided to the namespace through a Network Attachment Definiiton (NAD) using the same name as the UDN.

```
[root@acm41-jump ~]# oc get -n namespace-4 network-attachment-definitions
NAME          AGE
primary-udn   2d18h
[root@acm41-jump ~]#
```

**Note:** Only one primary UDN can be created in any namespace. If a user wanted to use additional networks, secondary networks must have been created and provisioned in addition.

## 4. Create VMs using the new local network

The automatically applied NAD to the namespace configured implies that the default network for the VM is used with this NAD and thus the UDN. No additional pod network will be used for the VM NIC as it would be with adding additional NADs manually. The user is free to add other networks as needed in addition to the UDN created.

Create two VMs using the same namespace but the new local network resource, the UDN, for communication. This is done automatically for the VMs inside this namespace and doesn't require additional configuration, at least from network config side.

Create a file for the VM configuration, like here in the file `nad-namespace-vm4-l2nad.yaml`:

```
!!!include(nad-namespace-vm4-l2nad.yaml)!!!
```

Create the VM.

```
oc create -f nad-namespace-vm4-l2nad.yaml
```

Create another VM inside the same namespace like the one before.
From the code example above, the VM name should be changed in all occurences to e.g. rhel8-vm5.\

## Check communication

Record the network address assigned to the VM on the default network on the VM overview.

```
[root@acm41-jump ns-4]# oc get -n namespace-4 vm,vmi
NAME                                   AGE   STATUS    READY
virtualmachine.kubevirt.io/rhel8-vm4   43s   Running   True
virtualmachine.kubevirt.io/rhel8-vm5   36s   Running   True

NAME                                           AGE   PHASE     IP             NODENAME                    READY
virtualmachineinstance.kubevirt.io/rhel8-vm4   38s   Running   192.168.21.3   master0.acm41.dslab.local   True
virtualmachineinstance.kubevirt.io/rhel8-vm5   32s   Running   192.168.21.4   master0.acm41.dslab.local   True
[root@acm41-jump ns-4]#
```

Login to the console of one of the newly created VMs and check check with ping the network connection is working.

```
[root@acm41-jump ns-4]# virtctl console -n namespace-4 rhel8-vm4
Successfully connected to rhel8-vm4 console. The escape sequence is ^]

Red Hat Enterprise Linux 8.10 (Ootpa)
Kernel 4.18.0-553.70.1.el8_10.x86_64 on an x86_64

Activate the web console with: systemctl enable --now cockpit.socket

rhel8-vm4 login: cloud-user
Password:
[cloud-user@rhel8-vm4 ~]$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1342 qdisc fq_codel state UP group default qlen 1000
    link/ether 0a:58:c0:a8:15:03 brd ff:ff:ff:ff:ff:ff
    altname enp1s0
    inet 192.168.21.3/24 brd 192.168.21.255 scope global dynamic noprefixroute eth0
       valid_lft 2413sec preferred_lft 2413sec
    inet6 fe80::858:c0ff:fea8:1503/64 scope link noprefixroute
       valid_lft forever preferred_lft forever
[cloud-user@rhel8-vm4 ~]$ ping 192.168.21.4
PING 192.168.21.4 (192.168.21.4) 56(84) bytes of data.
64 bytes from 192.168.21.4: icmp_seq=1 ttl=64 time=6.48 ms
64 bytes from 192.168.21.4: icmp_seq=2 ttl=64 time=4.02 ms
64 bytes from 192.168.21.4: icmp_seq=3 ttl=64 time=1.01 ms

--- 192.168.21.4 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 1.006/3.836/6.481/2.240 ms
[cloud-user@rhel8-vm4 ~]$ exit
logout

Red Hat Enterprise Linux 8.10 (Ootpa)
Kernel 4.18.0-553.70.1.el8_10.x86_64 on an x86_64

Activate the web console with: systemctl enable --now cockpit.socket

rhel8-vm4 login: [root@acm41-jump ns-4]#
...
```

## Check IP addresses and communication one of the VMs is live migrated to another node

Check the current location the VMs and start live migration of one of the VMs.
Login to the VM migrated and try to ping the peer VM. Check that the VM got migrated to another node. There should be no change to IP address or the migrated VM and the peer VM should be reachable still using ping.

Example:

```
[root@acm41-jump ns-4]# oc get -n namespace-4 vmi
NAME        AGE   PHASE     IP             NODENAME                    READY
rhel8-vm4   24m   Running   192.168.21.3   master1.acm41.dslab.local   True
rhel8-vm5   24m   Running   192.168.21.4   master1.acm41.dslab.local   True
[root@acm41-jump ns-4]# virtctl migrate rhel8-vm4
VM rhel8-vm4 was scheduled to migrate
[root@acm41-jump ns-4]# oc get -n namespace-4 vmi
NAME        AGE   PHASE     IP             NODENAME                    READY
rhel8-vm4   25m   Running   192.168.21.3   master0.acm41.dslab.local   True
rhel8-vm5   25m   Running   192.168.21.4   master1.acm41.dslab.local   True
[root@acm41-jump ns-4]# virtctl console -n namespace-4 rhel8-vm4
Successfully connected to rhel8-vm4 console. The escape sequence is ^]

Red Hat Enterprise Linux 8.10 (Ootpa)
Kernel 4.18.0-553.70.1.el8_10.x86_64 on an x86_64

Activate the web console with: systemctl enable --now cockpit.socket

rhel8-vm4 login: cloud-user
Password:
Last login: Fri Oct 10 07:19:28 on ttyS0
[cloud-user@rhel8-vm4 ~]$ ping 192.168.21.4
PING 192.168.21.4 (192.168.21.4) 56(84) bytes of data.
64 bytes from 192.168.21.4: icmp_seq=1 ttl=64 time=8.58 ms
64 bytes from 192.168.21.4: icmp_seq=2 ttl=64 time=4.25 ms
64 bytes from 192.168.21.4: icmp_seq=3 ttl=64 time=1.28 ms

--- 192.168.21.4 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2004ms
rtt min/avg/max/mdev = 1.278/4.702/8.579/2.997 ms
[cloud-user@rhel8-vm4 ~]$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1342 qdisc fq_codel state UP group default qlen 1000
    link/ether 0a:58:c0:a8:15:03 brd ff:ff:ff:ff:ff:ff
    altname enp1s0
    inet 192.168.21.3/24 brd 192.168.21.255 scope global dynamic noprefixroute eth0
       valid_lft 2042sec preferred_lft 2042sec
    inet6 fe80::858:c0ff:fea8:1503/64 scope link noprefixroute
       valid_lft forever preferred_lft forever
[cloud-user@rhel8-vm4 ~]$ exit
logout

Red Hat Enterprise Linux 8.10 (Ootpa)
Kernel 4.18.0-553.70.1.el8_10.x86_64 on an x86_64

Activate the web console with: systemctl enable --now cockpit.socket

rhel8-vm4 login: [root@acm41-jump ns-4]#
```
