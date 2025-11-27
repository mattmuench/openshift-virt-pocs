# MTV vSphere vddk preparation

## Download vddk and prepare a Dockerfile

Go to https://developer.broadcom.com/sdks/vmware-virtual-disk-development-kit-vddk/latest and download the Linux version of the kit appropriate to your installed vSphere / ESXi version.

Unpack the file and create the Dockerfile:

```
[username@clustername-jump vddk]$ tar xzf VMware-vix-disklib-9.0.1.0.24964809.x86_64.tar.gz

```

## Check for or install podman on the workstation used for generating the vddk image

```
[root@clustername-jump vddk]# podman version
Client:       Podman Engine
Version:      5.6.0
API Version:  5.6.0
Go Version:   go1.24.6 (Red Hat 1.24.6-1.el9)
Built:        Mon Nov 10 09:54:39 2025
OS/Arch:      linux/amd64
[root@clustername-jump vddk]#
```

Alternatively, if podman isn't installed, install it:

```
sudo dnf install podman
```

## Prepare the cluster for upload of the image

### Make sure the internal registry is enabled and configured with stable storage

Change the image registry from `Remove` to `Managed`:

```
[username@clustername-jump vddk]$ oc patch configs.imageregistry.operator.openshift.io cluster --type merge --patch '{"spec":{"managementState":"Managed"}}'
config.imageregistry.operator.openshift.io/cluster patched
[username@clustername-jump vddk]$
```

### Configure stable storage to the registry:

```
[username@clustername-jump vddk]$ oc patch configs.imageregistry.operator.openshift.io cluster --type merge --patch '{"spec":{"storage":{"pvc":{"claim":""}}}}'
config.imageregistry.operator.openshift.io/cluster patched
[username@clustername-jump vddk]$
```

### Enable the external access to internal registry:

```
[username@clustername-jump vddk]$ oc patch configs.imageregistry.operator.openshift.io/cluster --type merge -p '{"spec":{"defaultRoute":true}}'
config.imageregistry.operator.openshift.io/cluster patched
[username@clustername-jump vddk]$
```

## Build the image and upload it

```
cat > Dockerfile <<EOF
FROM registry.access.redhat.com/ubi8/ubi-minimal
USER 1001
COPY vmware-vix-disklib-distrib /vmware-vix-disklib-distrib
RUN mkdir -p /opt
ENTRYPOINT ["cp", "-r", "/vmware-vix-disklib-distrib", "/opt"]
EOF
```

## Get the actual configured imagestream for the vddk image from the MTV ForkliftController:

```
[root@clustername-jump vddk]# oc get -n openshift-mtv imagestream
NAME   IMAGE REPOSITORY                                                                   TAGS   UPDATED
vddk   default-route-openshift-image-registry.apps.clustername.labname.local/openshift-mtv/vddk
[root@clustername-jump vddk]#
```

## Build the image

```
[root@clustername-jump vddk]# podman build . -t $HOST/vddk:latest
STEP 1/5: FROM registry.access.redhat.com/ubi8/ubi-minimal
Trying to pull registry.access.redhat.com/ubi8/ubi-minimal:latest...
Getting image source signatures
Checking if image destination supports signatures
Copying blob daf29424ccde done   |
Copying config fd5c121bbb done   |
Writing manifest to image destination
Storing signatures
STEP 2/5: USER 1001
--> f78e72835125
STEP 3/5: COPY vmware-vix-disklib-distrib /vmware-vix-disklib-distrib
--> f80b18189d40
STEP 4/5: RUN mkdir -p /opt
--> d0a64fe249ed
STEP 5/5: ENTRYPOINT ["cp", "-r", "/vmware-vix-disklib-distrib", "/opt"]
COMMIT default-route-openshift-image-registry.apps.clustername.labname.local/openshift-mtv/vddk:8.0.1
--> f813be42f32a
Successfully tagged default-route-openshift-image-registry.apps.clustername.labname.local/openshift-mtv/vddk:8.0.1
f813be42f32a2d1b2d38a7f64c2760ebd8836a73473c136a84deea180b59412e
[root@clustername-jump vddk]#
```

## Push the vddk image to the openshift image registry

```
[root@clustername-jump vddk]# podman login -u kubeadmin -p sha256~KbwutiztpSWhkN8BDvxcSIOB98p42X3RdrNMGBphfzg $HOST
Login Succeeded!
[root@clustername-jump vddk]# podman push --tls-verify=false default-route-openshift-image-registry.apps.clustername.labname.local/openshift-mtv/vddk:8.0.1
Getting image source signatures
Copying blob 5a74e48533a1 done   |
Copying blob 5f70bf18a086 done   |
Copying blob 356afc6426fa done   |
Copying config f813be42f3 done   |
Writing manifest to image destination
[root@clustername-jump vddk]#
```
