# octopus

## sdnChecker

An application to check SDN connectivity between each nodes in cluster
periodically.

Pods will be deployed via daemonSets to make sure every nodes (Master and
Node) will have one running on it. Nodes should be labelled with "sdnChecking=true".

Check sdnChecker/deploy.sh for more operation details.

## dupvipmonitor

An application to check whether there are some duplicated VIPs in cluster
periodically.

Only one pod in deploymentCOnfigs. And for deployment sucessfully, at least
one node, where has no VIP on it, should be labelled with "dupvipmonitor=true".

## PLAN

Plan to write a tool to analyze networking issues for our CaaS platform.
