# Creating local private networks for VMs at scale - cluster wide - using the CLI

Goal: As an administrator, I want to create private networks for VMs at scale to be consumed across namespaces that VMs can communicate on without the need of an additional network and no external access. I want to use the CLI only.

# **However, this will not work with VMs!**

An overview is available in [Overview to local networks](udn-overview.md).

Clusterwide NADs can be used to provide an isolated local network that is not using the pod subnet, especially if there is no additional external network available. This is useful if an administrator needs to isolate any communication between pods or VMs but allow communication across different namespaces. However, in contrast to layer 2 networks, layer 3 networks might be useful when numerous pods and VMs must communicate and IP address limitation might be an issue.
It helps in case the application spans multiple namespaces because of different repsonsibilities for application parts.

Due to the nature of the layer 3 network being distributed as subnet ranges per involved node, the IP address will change under these conditions:

- restart of a VM/pod and scheduling on another node
- live migration of a VM

Because of changes of the IP address, the useability for VMs is limited under normal conditions. However, even the overall high number of VMs on a single network could be questionable. In any case, if the desire is there, any measures to get to the right VM must be taken in order to let the communication peers understand the actual IP address of an instance. A measure could be to configure a load balancer to cover a whole network if the VMs in question form a scalable service.

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

Example namespace defintion is created here in the file `udn-l3-cluster-namespace-with-udn.yaml`

```
!!!include(udn-l3-cluster-namespace-with-udn.yaml)!!!
```

Create the new namespace.

```
oc create -f udn-l3-cluster-namespace-with-udn.yaml
```

Create a second namespace similar to the code example above.

## 2. Optional: Inform yourself about networks in use with the individual hypervisor cluster

Since the UDN traffic is encapsulated anyways when travelling over the cluster and host network, there shouldn't be any clashes. However, using different CIDRs might ease any troubleshooting when not having overlapping use of CIDRs in different layers of the network.

Prepare for creating a UDN with a specific CIDR. The IP addresses for the VMs in primary UDNs with a layer 2 topology are provided automatically. A VM would need to use DHCP to configure the network interface in order to be able to use the layer 3 network properly. Those assigned IP addresses will be only retained automatically within a given host to avoid handing out the same IP address to different instance upon reboot or migrating VMs - on another node, a VM will receive a new IP address from the sepcified subnet and host segment.

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

One must create a network resource to consume it with VMs (and pods). Layer 3 UDNs assign an IP address automatically for the VMs from the subnet specified but from the individual the host segment. The IP address of a VM will be not retained throughout the lifecycle of the VM.

**Note:** Up to OpenShift version 4.19, the local network resource must be created upfront. Later versions of OpenShift might allow an on-the-fly creation of the network resource at the time of a VM creation.

A VM would need to use DHCP to configure the network interface in order to be able to use the layer 3 network properly. However, due to the nature of the layer 3 network, those assigned IP addresses will not be retained.

Create a file for the UDN configuration, like here in the file `udn-l3-cluster-udn.yaml`:

```
!!!include(udn-l3-cluster-udn.yaml)!!!
```

Create the new udn resource.

```
oc create -f udn-l3-cluster-udn.yaml
```

Check the resource is being created.

```
[root@acm41-jump ns-7]# oc get -A clusteruserdefinednetwork
NAME                     AGE
udn-cluster-primary-l3   25s
[root@acm41-jump ns-7]#
```

Once a cluster scoped UDN is configured, automatically it's provided to the namespaces through a Network Attachment Definiton (NAD) using the same name as the UDN.

```
[root@acm41-jump ns-7]# oc get -n namespace-7 network-attachment-definitions
NAME                     AGE
udn-cluster-primary-l3   70s
[root@acm41-jump ns-7]# oc get -n namespace-8 network-attachment-definitions
NAME                     AGE
udn-cluster-primary-l3   78s
[root@acm41-jump ns-7]#
```

**Note:** Only one primary UDN can be created in any namespace. If a user wanted to use additional networks, secondary networks must have been created and provisioned in addition.

## 4. Create VMs using the new local network

The automatically applied NAD to the namespace configured, being the primary network, implies that the default network for the VM is used with this NAD and thus the UDN. The pod network will be used for the VM to communicate as it would be with adding additional NADs manually. The user is free to add other networks as needed in addition to the UDN created.

Create two VMs using different same namespaces but the new local network resource, the UDN, for communication. This is done automatically for the VMs inside those namespaces and doesn't require additional configuration, at least from network config side.

Create a file for the VM configuration, like here in the file `udn-cluster-vm6-l2udn.yaml`:

```
!!!include(udn-cluster-vm8-l3udn.yaml)!!!
```

Create the VM and check for the VM being created. Record the IP address assigned to the VM as primary IP address.

```
[root@acm41-jump ns-7]# oc apply -f vm8-ns7.yaml
virtualmachine.kubevirt.io/rhel8-vm8 created
[root@acm41-jump ns-7]#
[root@acm41-jump ns-7]# oc -n namespace-7 get vm,vmi
NAME                                   AGE   STATUS    READY
virtualmachine.kubevirt.io/rhel8-vm8   47s   Running   True

NAME                                           AGE   PHASE     IP             NODENAME                    READY
virtualmachineinstance.kubevirt.io/rhel8-vm8   43s   Running   192.168.24.6   master1.acm41.dslab.local   True
[root@acm41-jump ns-7]#
```

Create another VM inside the other namespace like the one before.
From the code example above, the VM name should be changed in all occurences to e.g. rhel8-vm7 but also the namespace must be changed to the other namespace.
Check for the VM being created. Record the IP address assigned to the VM as primary IP address.

```
[root@acm41-jump ns-7]# oc -n namespace-8 get vm,vmi
NAME                                   AGE   STATUS    READY
virtualmachine.kubevirt.io/rhel8-vm9   44s   Running   True

NAME                                           AGE   PHASE     IP              NODENAME                    READY
virtualmachineinstance.kubevirt.io/rhel8-vm9   40s   Running   192.168.24.11   master1.acm41.dslab.local   True
[root@acm41-jump ns-7]#
```

Note that both VMs running in different namespaces but having an IP address automatically assign from the desired IP subnet. Note also that both VMs are created on the same host, which is by fortune.

## Check communication

Record the network addresses assigned to the VMs on the default network - on the VM listings from above.

Login to the console of one of the newly created VMs and check with ping that the network connection is working.

```
[root@acm41-jump ns-5]# virtctl console -n namespace-5 rhel8-vm6
Successfully connected to rhel8-vm6 console. The escape sequence is ^]

Red Hat Enterprise Linux 8.10 (Ootpa)
Kernel 4.18.0-553.77.1.el8_10.x86_64 on an x86_64

Activate the web console with: systemctl enable --now cockpit.socket

rhel8-vm6 login: cloud-user
Password:
[cloud-user@rhel8-vm6 ~]$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
inet 127.0.0.1/8 scope host lo
valid_lft forever preferred_lft forever
inet6 ::1/128 scope host
valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1342 qdisc fq_codel state UP group default qlen 1000
link/ether 0a:58:c0:a8:16:03 brd ff:ff:ff:ff:ff:ff
altname enp1s0
inet 192.168.22.3/24 brd 192.168.22.255 scope global dynamic noprefixroute eth0
valid_lft 3081sec preferred_lft 3081sec
inet6 fe80::858:c0ff:fea8:1603/64 scope link noprefixroute
valid_lft forever preferred_lft forever
[cloud-user@rhel8-vm6 ~]$ ping 192.168.22.4
PING 192.168.22.4 (192.168.22.4) 56(84) bytes of data.
64 bytes from 192.168.22.4: icmp_seq=1 ttl=64 time=10.7 ms
64 bytes from 192.168.22.4: icmp_seq=2 ttl=64 time=34.4 ms
64 bytes from 192.168.22.4: icmp_seq=3 ttl=64 time=2.22 ms
64 bytes from 192.168.22.4: icmp_seq=4 ttl=64 time=0.909 ms
64 bytes from 192.168.22.4: icmp_seq=5 ttl=64 time=2.72 ms

--- 192.168.22.4 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 4020ms
rtt min/avg/max/mdev = 0.909/10.204/34.428/12.595 ms
[cloud-user@rhel8-vm6 ~]$
```

## Check IP addresses and communication after one of the VMs is live migrated to another node

Check the current location of the VMs and start live migration of one of the VMs.
Login to the VM migrated and try to ping the peer VM. Check that the VM got migrated to another node. There should be no change to IP address and the migrated VM and the peer VM should be reachable still using ping.

Example:

```
[root@acm41-jump ns-5]# oc get -n namespace-5 vmi
NAME        AGE   PHASE     IP             NODENAME                    READY
rhel8-vm6   18m   Running   192.168.22.3   master1.acm41.dslab.local   True
[root@acm41-jump ns-5]# oc get -n namespace-6 vmi
NAME        AGE   PHASE     IP             NODENAME                    READY
rhel8-vm7   15m   Running   192.168.22.4   master1.acm41.dslab.local   True
[root@acm41-jump ns-5]#
```

In this case, both VMs running on master1. Now, migrate the VM rhel8-vm6. Check for the new location and make sure that the other VM didn't migrate silently.

```
[root@acm41-jump ~]# oc get vmi
NAME        AGE   PHASE     IP             NODENAME                    READY
rhel8-vm8   21h   Running   192.168.24.6   master1.acm41.dslab.local   True
[root@acm41-jump ~]# oc get -n namespace-8 vmi
NAME        AGE   PHASE     IP              NODENAME                    READY
rhel8-vm9   21h   Running   192.168.24.11   master1.acm41.dslab.local   True
[root@acm41-jump ~]# virtctl migrate rhel8-vm8
VM rhel8-vm8 was scheduled to migrate
[root@acm41-jump ~]# oc get vmi
NAME        AGE   PHASE     IP             NODENAME                    READY
rhel8-vm8   21h   Running   192.168.24.6   master1.acm41.dslab.local   True
[root@acm41-jump ~]# oc get vmi
NAME        AGE   PHASE     IP             NODENAME                    READY
rhel8-vm8   21h   Running   192.168.24.6   master1.acm41.dslab.local   True
[root@acm41-jump ~]# oc get vmi
NAME        AGE   PHASE     IP             NODENAME                    READY
rhel8-vm8   21h   Running   192.168.24.6   master1.acm41.dslab.local   True
[root@acm41-jump ~]# oc get vm,vmi
NAME                                   AGE   STATUS    READY
virtualmachine.kubevirt.io/rhel8-vm8   21h   Running   True

NAME                                           AGE   PHASE     IP               NODENAME                    READY
virtualmachineinstance.kubevirt.io/rhel8-vm8   21h   Running   192.168.24.132   master2.acm41.dslab.local   True
[root@acm41-jump ~]# oc get vmi
NAME        AGE   PHASE     IP               NODENAME                    READY
rhel8-vm8   21h   Running   192.168.24.132   master2.acm41.dslab.local   True
[root@acm41-jump ~]#
```

Check connectivity from the VM to the other VM

```
[root@acm41-jump ns-5]# virtctl console -n namespace-5 rhel8-vm6
Successfully connected to rhel8-vm6 console. The escape sequence is ^]

Red Hat Enterprise Linux 8.10 (Ootpa)
Kernel 4.18.0-553.77.1.el8_10.x86_64 on an x86_64

Activate the web console with: systemctl enable --now cockpit.socket

rhel8-vm6 login: cloud-user
Password:
Last login: Mon Oct 20 10:10:09 on ttyS0
[cloud-user@rhel8-vm6 ~]$ ping 192.168.22.4
PING 192.168.22.4 (192.168.22.4) 56(84) bytes of data.
64 bytes from 192.168.22.4: icmp_seq=1 ttl=64 time=10.5 ms
64 bytes from 192.168.22.4: icmp_seq=2 ttl=64 time=6.19 ms
64 bytes from 192.168.22.4: icmp_seq=3 ttl=64 time=4.79 ms

--- 192.168.22.4 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2004ms
rtt min/avg/max/mdev = 4.792/7.148/10.465/2.413 ms
[cloud-user@rhel8-vm6 ~]$
```
