## flask thread/workers

https://stackoverflow.com/questions/38876721/handle-flask-requests-concurrently-with-threaded-true

> Normally, the WSGI server included with Flask is run in single-threaded mode, and can only handle one request at a time. Any parallel requests will have to wait until they can be handled, which can lead to issues if you tried to contact your own server from a request.
    
 > With threaded=True requests are each handled in a new thread. How many threads your server can handle concurrently depends entirely on your OS and what limits it sets on the number of threads per process. The implementation uses the SocketServer.ThreadingMixIn class, which sets no limits to the number of threads it can spin up.
    
> Note that the Flask server is designed for development only. It is not a production-ready server. Don't rely on it to run your site on the wider web. Use a proper WSGI server like gunicorn or uWSGI) instead.
    
## Dockerfile COPY vs ADD

https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#add-or-copy

> Although ADD and COPY are functionally similar, generally speaking, COPY is preferred. That’s because it’s more transparent than ADD. COPY only supports the basic copying of local files into the container, while ADD has some features (like local-only tar extraction and remote URL support) that are not immediately obvious. Consequently, the best use for ADD is local tar file auto-extraction into the image, as in ADD rootfs.tar.xz /.

> If you have multiple Dockerfile steps that use different files from your context, COPY them individually, rather than all at once. This ensures that each step’s build cache is only invalidated (forcing the step to be re-run) if the specifically required files change.

https://docs.docker.com/engine/reference/builder/#copy

> If multiple <src> resources are specified, either directly or due to the use of a wildcard, then <dest> must be a directory, and it must end with a slash /.

## Dockerfile CMD vs ENTRYPOINT

https://stackoverflow.com/questions/21553353/what-is-the-difference-between-cmd-and-entrypoint-in-a-dockerfile

> Docker has a default entrypoint which is /bin/sh -c but does not have a default command.

> When you run docker like this: docker run -i -t ubuntu bash the entrypoint is the default /bin/sh -c, the image is ubuntu and the command is bash.

> The command is run via the entrypoint. i.e., the actual thing that gets executed is /bin/sh -c bash. This allowed Docker to implement RUN quickly by relying on the shell's parser.

> Later on, people asked to be able to customize this, so ENTRYPOINT and --entrypoint were introduced.

> Everything after ubuntu in the example above is the command and is passed to the entrypoint. When using the CMD instruction, it is exactly as if you were doing docker run -i -t ubuntu <cmd>. <cmd> will be the parameter of the entrypoint.

> You will also get the same result if you instead type this command docker run -i -t ubuntu. You will still start a bash shell in the container because of the ubuntu Dockerfile specified a default CMD: CMD ["bash"]

> As everything is passed to the entrypoint, you can have a very nice behavior from your images. @Jiri example is good, it shows how to use an image as a "binary". When using ["/bin/cat"] as entrypoint and then doing docker run img /etc/passwd, you get it, /etc/passwd is the command and is passed to the entrypoint so the end result execution is simply /bin/cat /etc/passwd.

> Another example would be to have any cli as entrypoint. For instance, if you have a redis image, instead of running docker run redisimg redis -H something -u toto get key, you can simply have ENTRYPOINT ["redis", "-H", "something", "-u", "toto"] and then run like this for the same result: docker run redisimg get key.

## OpenShift API

Get pods in a namespace
https://docs.openshift.com/container-platform/3.9/rest_api/api/v1.Pod.html#Get-api-v1-namespaces-namespace-pods

Get all hostsubnets
https://docs.openshift.com/container-platform/3.9/rest_api/apis-network.openshift.io/v1.HostSubnet.html#Get-apis-network.openshift.io-v1-hostsubnets


## OpenShift SCC

https://docs.openshift.com/container-platform/3.9/admin_guide/manage_scc.html#example-security-context-constraints

> When a container or pod does not request a user ID under which it should be run, the effective UID depends on the SCC that emits this pod. Because restricted SCC is granted to all authenticated users by default, it will be available to all users and service accounts and used in most cases. The restricted SCC uses MustRunAsRange strategy for constraining and defaulting the possible values of the securityContext.runAsUser field. The admission plug-in will look for the openshift.io/sa.scc.uid-range annotation on the current project to populate range fields, as it does not provide this range. In the end, a container will have runAsUser equal to the first value of the range that is hard to predict because every project has different ranges. See Understanding Pre-allocated Values and Security Context Constraints(https://docs.openshift.com/container-platform/3.9/architecture/additional_concepts/authorization.html#understanding-pre-allocated-values-and-security-context-constraints) for more information.

> A container or pod that requests a specific user ID will be accepted by OpenShift Container Platform only when a service account or a user is granted access to a SCC that allows such a user ID. The SCC can allow arbitrary IDs, an ID that falls into a range, or the exact user ID specific to the request.

https://docs.openshift.com/container-platform/3.9/admin_guide/manage_scc.html#enable-images-to-run-with-user-in-the-dockerfile

> Grant all authenticated users access to the anyuid SCC:

    $ oc adm policy add-scc-to-group anyuid system:authenticated

> This allows images to run as the root UID if no USER is specified in the Dockerfile.

## OpenShift RBAC

A appropriate role can be find here:
https://docs.openshift.com/container-platform/3.9/admin_guide/manage_rbac.html

## Other interesting things

https://medium.com/@lmakarov/the-backlash-of-chmod-chown-mv-in-your-dockerfile-f12fe08c0b55

> Every command in a Dockerfile runs in a separate (intermediate) container. The results are then stored as a new image layer on top of the existing ones. Adding a file in one layer and then removing, replacing or even moving it in another layer does not remove the original file from the underlying layer. Think of layers as of Git commits — a file is preserved in the git history even after you remove it from the repo.

> Updating ownership on a file with chown effectively results in duplicating that file and storing its new copy in a new layer. The original copy is still there in the underlying layer. The same applies to chmod and even mv commands. When using them in your Dokerfile, you may end up with an inflated image, before you realize what’s going on.

> Starting with Docker 17.09.0-ce (2017–09–26) ADD/COPY commands now support the—-chown flag in Dockerfile:

    COPY --chown=docker:docker source /path/to/destination
