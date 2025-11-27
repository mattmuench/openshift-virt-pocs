# Using MTV for migrating VMs

## 1 Prepare the cluster for incoming VMs

The external dependencies must be prepared.

- A direct network connection between the source and destination cluster must exist - in non-PoC env, also other ways of linking the both clusters might be used.

- for vSphere, open the port according to the table 4.2 in [=> Network ports to open](https://docs.redhat.com/en/documentation/migration_toolkit_for_virtualization/2.10/html/planning_your_migration_to_red_hat_openshift_virtualization/assembly_prerequisites-for-migration_mtv#ports_mtv)

- for vSphere, create a role to a facilitate the migration from a vSphere cluster - apply the priviledges from table 4.11.1 [=> vSphere role priviledges](https://docs.redhat.com/en/documentation/migration_toolkit_for_virtualization/2.10/html/planning_your_migration_to_red_hat_openshift_virtualization/assembly_prerequisites-for-migration_mtv#vmware-privileges_mtv) and create apply it to **inventory** section [=> like in VMware role](https://docs.redhat.com/en/documentation/migration_toolkit_for_virtualization/2.10/html/planning_your_migration_to_red_hat_openshift_virtualization/assembly_prerequisites-for-migration_mtv#creating-vmware-role-mtv-permissions_mtv)

## 2 Prepare the migration toolkit

### 2.1 Install MTV and enable the ForliftController

The Migration Toolkit for Virtualization must be installed prior to any further configuration for migration.  
[=> see: MTV installation using the console](installation/mtv-install-using-console/mtv-install-console.md)

### 2.2 Define the destination provider

Since the MTV could run somewhere and not on neccesarily on the destination cluster, this step is required in order to know where the migration should be performed to.

Also, one could have a single MTV controlling all other migrations between various sources and destinations.

To create one for the local OpenShift Virtualization cluster:
[=> see: MTV provider for the local Openshift Virtualization](mtv-provider-ocp/mtv-provider-ocp-console-local/mtv-provider-ocp-console-local.md)

To create one for an external cluster:
[=> see: MTV provider for Openshift Virtualization - does not work yet](dontuse-mtv-provider-ocp/mtv-provider-ocp-console/mtv-provider-ocp-console.md)

## 3 Prepare the source cluster for migrating VMs

Depending on the source cluster flavor, any of the following providers must be prepared.

[=> see: vSphere](mtv-provider-vsphere-console/mtv-provider-vsphere-console.md)

## 4 Check for requirements of VMs to be migrated

For vSphere, check that  
=> for **migration**:

- VMware tools must be installed
- disable hibernation of the VMs to migrate

=> for _warm_ **migration**. in addition check:

- CBT must be enabled for VMs and VM disks
- on Windows VMs enable VSS snapshots

For migrating more than 10 VMs per ESXi host:

- If you are migrating more than 10 VMs from an ESXi host in the same migration plan, you must increase the Network File Copy (NFC) service memory of the host.
