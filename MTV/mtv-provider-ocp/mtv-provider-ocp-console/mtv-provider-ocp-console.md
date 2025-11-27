# Create an OpenShift provider using the console

## Prepare a service account and service account bearer token with specific lifetime

**DOES NOT YET WORK**

```
[root@ocp68-jump ~]# oc create sa vm-migrate -n default
serviceaccount/vm-migrate created
[root@ocp68-jump ~]# oc adm policy add-role-to-user edit -z vm-migrate -n default
clusterrole.rbac.authorization.k8s.io/edit added: "vm-migrate"
[root@ocp68-jump ~]# oc create token vm-migrate --namespace default --duration 14400m > vm-migrate.token
[root@ocp68-jump ~]#
```

## Configure the provider

**All the steps can be carried out using the console.**

**In main menu, select `Migration for Virtualization` and there the submenu `Providers`. Create a new provider.**<br>
**From the supported list of migration sources, select OpenShift Virtualization. Keep the project as openshift-mtv.**<br><br>
![UI view MTV OpenShift Virtualization provider confiuration](images/mtv-provider-ocp-console-start.png)

<br><br>**Once selected , immediately the window for configuring it is displayed.** <br><br>
![UI view of OpenShift console to create UDNs](images/mtv-provider-ocp-console-select.png)

<br><br>**Fill in the config options:**

**- keep the project name as openshift-mtv**
**- keep the provider type as selected above - it will give the option to select another provider. This is misleading and should be not selected.**
**- provide a name for the resource - any descriptive name is fine**
**- select the endpoint type**
**- provide the URL to the OpenShift Virtualization cluster API as in https://dns.name.of.ocp-virt-cluster.domain:6443**

<br><br>**At this point, all information should be green - this doesn't say that it's correct but only the expected format of the values is correct:** <br><br>
![UI view of provider config](images/mtv-provider-ocp-console-config-1.png)

<br><br>**Enter your service account bearer token created in the very first step for the OpenShift cluster and add the certificate - alternatively, select to skip the certificate.** <br><br>
![UI view of provider crednetials](images/mtv-provider-vsphere-console-credentials.png)

<br><br>**Once all information is filled in, hit the `Create provider` button. It takes now a few seconds only and the `Ready` sign should be there.** <br><br>

# INCOMPLETE PART

![UI view of OpenShift console to create UDNs](images/mtv-provider-ocp-console-ready.png)

<br><br>**Further down in the overview for this new provider, the provider inventory should list the resources of the migration source:** <br><br>
![UI view of OpenShift console to create UDNs](images/unknown.png)

<br><br>**Now, on the main provider list, this new provider should be listed and should have `Ready` as the status.** <br><br>
![UI view of OpenShift console to create UDNs](images/unknown.png)
