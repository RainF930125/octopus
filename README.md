# octopus

## sdnChecker

An application to check SDN connectivity between each nodes in cluster
periodically.

Pods will be deployed via daemonSets to make sure every nodes (Master and
Node) will have one running on it. Nodes should be labelled with "sdnChecking=true".

Check sdnChecker/deploy.sh for more operation details.

## dupVIPMonitor

An application to check whether there are some duplicated VIPs in cluster
periodically.

Only one pod in deploymentCOnfigs. And for deployment sucessfully, at least
one node, where has no VIP on it, should be labelled with "dupvipmonitor=true".

Check dupVIPMonitor/deploy.sh for more operation details.

## tentacle

I have no idea how DynamicKubeletConfig works in origin, so I build this for
CMP to manage origin.

Possible modifiable configure options including max-pods, system-reserved,
cpuRequestToLimitPercent are tested, modification on them should not cause
origin-node or origin-master-api fails to restart.

And that's the idea to expose configure option for CMP, only tested, harmless.

## PLAN

Plan to write a tool to analyze networking issues for our CaaS platform.
