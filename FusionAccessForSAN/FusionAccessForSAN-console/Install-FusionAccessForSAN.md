# Installation of Fusion Access for SAN using the console and CLI

## Install the operator from operator hub

First supported and available version is for 4.19

**The operator installs into a single namespace but the operator install template says into every namespace**

## Create a pull secret using the software entitlement key

**Note: The entitlement key must have been requested and granted before the installation can proceed.**

```
echo '<entitlementkey>' > ibm-entitlement-key
[root@ocp68-jump fusion-access]#  oc create secret -n ibm-fusion-access generic fusion-pullsecret --from-literal=ibm-entitlement-key=ibm-entitlement-key
secret/fusion-pullsecret created
[root@ocp68-jump fusion-access]# oc get secret -n ibm-fusion-access
NAME                                                     TYPE                DATA   AGE
fusion-access-operator-controller-manager-service-cert   kubernetes.io/tls   3      21m
fusion-access-plugin-cert                                kubernetes.io/tls   2      21m
fusion-pullsecret                                        Opaque              1      5s
kmm-operator-webhook-service-cert                        kubernetes.io/tls   3      21m
metrics-service-cert                                     kubernetes.io/tls   2      21m
[root@ocp68-jump fusion-access]#
```

## Create the Fusion Access CR

!!!include(fusionfas-create-cr.png)!!!

Accept the default and click create.

!!!include(fusionfas-cr-created.png)!!!

Wait for the CR to become ready.

## Connect the external shared volumes to the worker nodes

**Note: all worker nodes must have access to the same shared volumes from the storage.**

### Configure storage to allow access from all OpenShift worker nodes to the storage.

> > On storage

### Configure access from the worker nodes to the storage

```
[root@ocp68-jump ~]# oc get nodes
NAME      STATUS   ROLES                         AGE   VERSION
master1   Ready    control-plane,master,worker   11h   v1.32.9
master2   Ready    control-plane,master,worker   12h   v1.32.9
master3   Ready    control-plane,master,worker   12h   v1.32.9
[root@ocp68-jump ~]# oc debug node/master1 -- chroot /host iscsiadm -m node -R
Starting pod/master1-debug-wd6jr ...
To use host binaries, run `chroot /host`. Instead, if you need to access host namespaces, run `nsenter -a -t 1`.
iscsiadm: No session found.

Removing debug pod ...
error: non-zero exit code from debug container
[root@ocp68-jump ~]#
[root@ocp68-jump ~]# oc debug node/master1 -- chroot /host lsblk|grep sd
Starting pod/master1-debug-pxhxc ...
To use host binaries, run `chroot /host`. Instead, if you need to access host namespaces, run `nsenter -a -t 1`.
sda      8:0    0   120G  0 disk
|-sda1   8:1    0     1M  0 part
|-sda2   8:2    0   127M  0 part
|-sda3   8:3    0   384M  0 part /boot
`-sda4   8:4    0 119.5G  0 part /var

Removing debug pod ...
[root@ocp68-jump ~]#
[root@ocp68-jump ~]# oc debug node/master1
Starting pod/master1-debug-cmrkj ...
To use host binaries, run `chroot /host`. Instead, if you need to access host namespaces, run `nsenter -a -t 1`.
Pod IP: 172.21.68.11
If you don't see a command prompt, try pressing enter.
sh-5.1# chroot /host
sh-5.1# iscsiadm -m discovery -t st -p 172.21.11.69 -o new
172.21.11.69:3260,1 iqn.2005-10.org.freenas.ctl:infoscale2
sh-5.1# iscsiadm -m node --login
Logging in to [iface: default, target: iqn.2005-10.org.freenas.ctl:infoscale2, portal: 172.21.11.69,3260]
Login to [iface: default, target: iqn.2005-10.org.freenas.ctl:infoscale2, portal: 172.21.11.69,3260] successful.
sh-5.1# lsblk
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0    7:0    0   5.8M  1 loop
sda      8:0    0   120G  0 disk
|-sda1   8:1    0     1M  0 part
|-sda2   8:2    0   127M  0 part
|-sda3   8:3    0   384M  0 part /boot
`-sda4   8:4    0 119.5G  0 part /var
                                 /sysroot/ostree/deploy/rhcos/var
                                 /sysroot
                                 /etc
sdb      8:16   0     2G  0 disk
sdc      8:32   0   213M  0 disk
sdd      8:48   0   140G  0 disk
sde      8:64   0     2G  0 disk
sdf      8:80   0     2G  0 disk
sr0     11:0    1     2K  0 rom
sh-5.1# scsiadm -m node --targetname iqn.2005-10.org.freenas.ctl:infoscale2 --portal 172.21.11.69 --logout
sh: scsiadm: command not found
sh-5.1# iscsiadm -m node --targetname iqn.2005-10.org.freenas.ctl:infoscale2 --portal 172.21.11.69 --logout
Logging out of session [sid: 1, target: iqn.2005-10.org.freenas.ctl:infoscale2, portal: 172.21.11.69,3260]
Logout of [sid: 1, target: iqn.2005-10.org.freenas.ctl:infoscale2, portal: 172.21.11.69,3260] successful.
sh-5.1# iscsiadm -m node --targetname iqn.2005-10.org.freenas.ctl:infoscale2 --portal 172.21.11.69 --op=delete
sh-5.1# iscsiadm 0m node
Try `iscsiadm --help' for more information.
sh-5.1# iscsiadm -m node
iscsiadm: No records found
sh-5.1# lsblk
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0    7:0    0   5.8M  1 loop
sda      8:0    0   120G  0 disk
|-sda1   8:1    0     1M  0 part
|-sda2   8:2    0   127M  0 part
|-sda3   8:3    0   384M  0 part /boot
`-sda4   8:4    0 119.5G  0 part /var
                                 /sysroot/ostree/deploy/rhcos/var
                                 /sysroot
                                 /etc
sr0     11:0    1     2K  0 rom
sh-5.1# iscsiadm -m discovery -t st -p 172.21.11.69 -o new
172.21.11.69:3260,1 iqn.2005-10.org.freenas.ctl:fusionbacking
sh-5.1# iscsiadm -m node --login
Logging in to [iface: default, target: iqn.2005-10.org.freenas.ctl:fusionbacking, portal: 172.21.11.69,3260]
Login to [iface: default, target: iqn.2005-10.org.freenas.ctl:fusionbacking, portal: 172.21.11.69,3260] successful.
sh-5.1# lsblk
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0    7:0    0   5.8M  1 loop
sda      8:0    0   120G  0 disk
|-sda1   8:1    0     1M  0 part
|-sda2   8:2    0   127M  0 part
|-sda3   8:3    0   384M  0 part /boot
`-sda4   8:4    0 119.5G  0 part /var
                                 /sysroot/ostree/deploy/rhcos/var
                                 /sysroot
                                 /etc
sdb      8:16   0   190G  0 disk
sr0     11:0    1     2K  0 rom
sh-5.1# exit
exit
sh-5.1# exit
exit

Removing debug pod ...
[root@ocp68-jump ~]# oc debug node/master2 -- chroot /host lsblk
Starting pod/master2-debug-5qrgb ...
To use host binaries, run `chroot /host`. Instead, if you need to access host namespaces, run `nsenter -a -t 1`.
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0    7:0    0   5.8M  1 loop
sda      8:0    0   120G  0 disk
|-sda1   8:1    0     1M  0 part
|-sda2   8:2    0   127M  0 part
|-sda3   8:3    0   384M  0 part /boot
`-sda4   8:4    0 119.5G  0 part /var/lib/kubelet/pods/f2740d5f-45b8-470e-be2d-13ce59839251/volume-subpaths/nginx-conf/networking-console-plugin/1
                                 /var
                                 /sysroot/ostree/deploy/rhcos/var
                                 /sysroot
                                 /etc
sr0     11:0    1     2K  0 rom

Removing debug pod ...
[root@ocp68-jump ~]# oc debug node/master2 -- chroot /host iscsiadm -m discovery -t st -p 172.21.11.69 -o new
Starting pod/master2-debug-bz68d ...
To use host binaries, run `chroot /host`. Instead, if you need to access host namespaces, run `nsenter -a -t 1`.
172.21.11.69:3260,1 iqn.2005-10.org.freenas.ctl:fusionbacking

Removing debug pod ...
[root@ocp68-jump ~]# iscsiadm -m node --login
-bash: iscsiadm: command not found
[root@ocp68-jump ~]# oc debug node/master2 -- chroot /host iscsiadm -m node --login
Starting pod/master2-debug-29799 ...
To use host binaries, run `chroot /host`. Instead, if you need to access host namespaces, run `nsenter -a -t 1`.
Logging in to [iface: default, target: iqn.2005-10.org.freenas.ctl:fusionbacking, portal: 172.21.11.69,3260]
Login to [iface: default, target: iqn.2005-10.org.freenas.ctl:fusionbacking, portal: 172.21.11.69,3260] successful.

Removing debug pod ...
[root@ocp68-jump ~]# oc debug node/master2 -- chroot /host lsblk
Starting pod/master2-debug-qvf8f ...
To use host binaries, run `chroot /host`. Instead, if you need to access host namespaces, run `nsenter -a -t 1`.
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0    7:0    0   5.8M  1 loop
sda      8:0    0   120G  0 disk
|-sda1   8:1    0     1M  0 part
|-sda2   8:2    0   127M  0 part
|-sda3   8:3    0   384M  0 part /boot
`-sda4   8:4    0 119.5G  0 part /var/lib/kubelet/pods/f2740d5f-45b8-470e-be2d-13ce59839251/volume-subpaths/nginx-conf/networking-console-plugin/1
                                 /var
                                 /sysroot/ostree/deploy/rhcos/var
                                 /sysroot
                                 /etc
sdb      8:16   0   190G  0 disk
sr0     11:0    1     2K  0 rom

Removing debug pod ...
[root@ocp68-jump ~]# oc debug node/master3 -- chroot /host lsblk
Starting pod/master3-debug-nq6s8 ...
To use host binaries, run `chroot /host`. Instead, if you need to access host namespaces, run `nsenter -a -t 1`.
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0    7:0    0   5.8M  1 loop
sda      8:0    0   120G  0 disk
|-sda1   8:1    0     1M  0 part
|-sda2   8:2    0   127M  0 part
|-sda3   8:3    0   384M  0 part /boot
`-sda4   8:4    0 119.5G  0 part /var/lib/kubelet/pods/548ef036-6c90-481b-bf5e-ca0ba88debbd/volume-subpaths/nginx-conf/networking-console-plugin/1
                                 /var
                                 /sysroot/ostree/deploy/rhcos/var
                                 /sysroot
                                 /etc
sr0     11:0    1     2K  0 rom

Removing debug pod ...
[root@ocp68-jump ~]# oc debug node/master3 -- chroot /host iscsiadm -m discovery -t st -p 172.21.11.69 -o new
Starting pod/master3-debug-57rtk ...
To use host binaries, run `chroot /host`. Instead, if you need to access host namespaces, run `nsenter -a -t 1`.
172.21.11.69:3260,1 iqn.2005-10.org.freenas.ctl:fusionbacking

Removing debug pod ...
[root@ocp68-jump ~]# oc debug node/master3 -- chroot /host 'iscsiadm -m node --login; lsblk'
Starting pod/master3-debug-fx45s ...
To use host binaries, run `chroot /host`. Instead, if you need to access host namespaces, run `nsenter -a -t 1`.
chroot: failed to run command 'iscsiadm -m node --login; lsblk': No such file or directory

Removing debug pod ...
error: non-zero exit code from debug container
[root@ocp68-jump ~]# oc debug node/master3 -- chroot /host iscsiadm -m node --login
Starting pod/master3-debug-kpjjt ...
To use host binaries, run `chroot /host`. Instead, if you need to access host namespaces, run `nsenter -a -t 1`.
Logging in to [iface: default, target: iqn.2005-10.org.freenas.ctl:fusionbacking, portal: 172.21.11.69,3260]
Login to [iface: default, target: iqn.2005-10.org.freenas.ctl:fusionbacking, portal: 172.21.11.69,3260] successful.

Removing debug pod ...
[root@ocp68-jump ~]# oc debug node/master3 -- chroot /host lsblk
Starting pod/master3-debug-4jcz2 ...
To use host binaries, run `chroot /host`. Instead, if you need to access host namespaces, run `nsenter -a -t 1`.
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0    7:0    0   5.8M  1 loop
sda      8:0    0   120G  0 disk
|-sda1   8:1    0     1M  0 part
|-sda2   8:2    0   127M  0 part
|-sda3   8:3    0   384M  0 part /boot
`-sda4   8:4    0 119.5G  0 part /var/lib/kubelet/pods/548ef036-6c90-481b-bf5e-ca0ba88debbd/volume-subpaths/nginx-conf/networking-console-plugin/1
                                 /var
                                 /sysroot/ostree/deploy/rhcos/var
                                 /sysroot
                                 /etc
sdb      8:16   0   190G  0 disk
sr0     11:0    1     2K  0 rom

Removing debug pod ...
[root@ocp68-jump ~]#
```

**Further installation:**

- https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/virtualization/index#creating-storage-cluster-fusion-access-san_install-configure-fusion-access-san
  or
- https://www.ibm.com/docs/en/fusion-software/2.11.0?topic=san-planning-prerequisites
