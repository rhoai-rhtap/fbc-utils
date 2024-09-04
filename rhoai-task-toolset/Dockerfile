FROM registry.access.redhat.com/ubi9/ubi-minimal:9.4-1134
RUN microdnf install -y git jq wget tar && \
    microdnf clean all && rm -rf /var/cache/dnf/*
RUN wget https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/openshift-client-linux.tar.gz && \
    tar xvf openshift-client-linux.tar.gz && chmod +x oc && mv oc /usr/local/bin/