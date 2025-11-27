# Installation and configuration of LVM storage

## Check local storage to be recognized as flash storage to avoid latency

```
oc debug node/master1.ocp03.single.demo.local -- chroot /host -c 'echo "ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/rotational}="0", ATTR{queue/scheduler}="none"" >/etc/udev/rules.d/90-non-rotational.rules'
```

## Installation of the operator

## Determine the h/w path of the device to use

```
[root@acm41-jump ~]# oc debug node/master1.acm41.dslab.local -- chroot /host ls -la /dev/disk/by-path/|grep sdd
Temporary namespace openshift-debug-qtf5q is created for debugging node...
Starting pod/master1acm41dslablocal-debug-wfbgf ...
To use host binaries, run `chroot /host`. Instead, if you need to access host namespaces, run `nsenter -a -t 1`.
lrwxrwxrwx. 1 root root   9 Oct  1 14:05 pci-0000:04:00.0-scsi-0:0:0:3 -> ../../sdd
Removing debug pod ...
Temporary namespace openshift-debug-qtf5q was removed.
[root@acm41-jump ~]#
```

or:

```
[core@master1 ~]$ ls -la /dev/disk/by-path/|grep sdb
lrwxrwxrwx. 1 root root   9 Nov 26 14:19 platform-PRL4010:00-ata-3 -> ../../sdb
lrwxrwxrwx. 1 root root   9 Nov 26 14:19 platform-PRL4010:00-ata-3.0 -> ../../sdb
[core@master1 ~]$
```

## Create the LVM cluster

Change the path to the device to what listed above. Note that the namespace must match `openshift-lvm-storage`.

```
apiVersion: lvm.topolvm.io/v1alpha1
kind: LVMCluster
metadata:
  name: my-lvmcluster
  namespace: openshift-lvm-storage
spec:
  tolerations:
  - effect: NoSchedule
    key: xyz
    operator: Equal
    value: "true"
  storage:
    deviceClasses:
    - name: vg1
      fstype: xfs
      default: true
      nodeSelector:
        nodeSelectorTerms:
        - matchExpressions:
          - key: kubernetes.io/hostname
            operator: In
            values:
            - master1.ocp03.single.demo.local
      deviceSelector:
        paths:
        - /dev/disk/by-path/platform-PRL4010:00-ata-3.0
        forceWipeDevicesAndDestroyAllData: true
      thinPoolConfig:
        name: thin-pool-1
        sizePercent: 90
        overprovisionRatio: 10
        chunkSize: 128Ki
        chunkSizeCalculationPolicy: Static
        metadataSize: 1Gi
        metadataSizeCalculationPolicy: Static
```

Create the cluster:

```
[focs@OCP3-gateway vddk]$ oc create -f lvm-storagecluster.yaml
lvmcluster.lvm.topolvm.io/my-lvmcluster created
[focs@OCP3-gateway vddk]$ oc get lvmcluster
NAME            STATUS
my-lvmcluster   Ready
[focs@OCP3-gateway vddk]$
```

```
[focs@OCP3-gateway vddk]$ oc get lvmvolumegroupnodestatus
NAME                              AGE
master1.ocp03.single.demo.local   2m13s
[focs@OCP3-gateway vddk]$ oc get lvmvolumegroup
NAME   AGE
vg1    2m48s
[focs@OCP3-gateway vddk]$
```

Check for the SC to be created:
[focs@OCP3-gateway vddk]$ oc get sc
NAME PROVISIONER RECLAIMPOLICY VOLUMEBINDINGMODE ALLOWVOLUMEEXPANSION AGE
lvms-vg1 (default) topolvm.io Delete WaitForFirstConsumer true 5m6s
[focs@OCP3-gateway vddk]$

Create a new storageclass
