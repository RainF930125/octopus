TEST_DOCKER_REGISTRY='harbor.testos39.com'
TEST_NAMESPACE='zp1dev'
TEST_LABEL_NODE='node2.os39.com'
TEST_VIPS='10.70.94.90,10.70.94.96'
TEST_DOCKER_REGISTRY_SECRET='zp1dev-pushsecret-harbor-testos39-com'
TEST_ROUTE='dupvipmonitor.testos39.com'

echo "This script is using:"
echo "    $TEST_DOCKER_REGISTRY as docker registry"
echo "    $TEST_NAMESPACE as namespace"
echo "    $TEST_VIPS as monitored VIPS"
echo "You should modify this script to use yours"
echo ""

oc project $TEST_NAMESPACE
oc create sa dupvipmonitor
oc secrets link dupvipmonitor $TEST_DOCKER_REGISTRY_SECRET --for=pull
oc adm policy add-scc-to-user privileged -z dupvipmonitor

docker build -t dupvipmonitor .
if [[ $? -ne 0 ]]; then
    echo "Failed to build image. Exit"
    exit 1
fi
docker tag dupvipmonitor $TEST_DOCKER_REGISTRY/$TEST_NAMESPACE/dupvipmonitor:v1
docker push $TEST_DOCKER_REGISTRY/$TEST_NAMESPACE/dupvipmonitor:v1

echo "!!!"
echo "!!! ARPING_INTERVAL(default 0.2s) defines interval to send arping packets, currently not set"
echo "!!! MONITOR_INTERVAL(default 6s) defines interval to do check for all vips, currently not set"
echo "!!!"

oc get node $TEST_LABEL_NODE -o=jsonpath='{.metadata.labels}' | grep -q "dupvipmonitor:true"
if [[ $? -ne 0 ]]; then
    oc label node $TEST_LABEL_NODE dupvipmonitor=true
fi

sed "s/TEST_DOCKER_REGISTRY/$TEST_DOCKER_REGISTRY/g" dupvipmonitor.yml > dupvipmonitor-test.yml
sed -i "s/TEST_NAMESPACE/$TEST_NAMESPACE/g" dupvipmonitor-test.yml
sed -i "s/TEST_ROUTE/$TEST_ROUTE/g" dupvipmonitor-test.yml
sed -i "s/TEST_VIPS/$TEST_VIPS/g" dupvipmonitor-test.yml
oc create -f dupvipmonitor-test.yml
