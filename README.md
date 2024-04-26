# File-Based Catalog Utilities

This is a collection of scripts that will help you to manage a File-Based Catalog (FBC) that will be used by the Operator Lifecycle Manager (OLM) in OpenShift to update your operator.

Some parts of this toolset will only make sense if you're building your FBC through Konflux, but in theory most of it is build-system independent. Another assumption is that your container images are eventually published through the Red Hat Container Ecosystem registry (`registry.redhat.io`).

The current state of things is a bit rough. The scripts were developed for [RHBK product](https://github.com/rhbk/rhbk-fbc)'s use with an eye to making them generally useful, but they may not fit your exact purpose unless it's identical to RHBK's. Pull Requests are welcome!

## Setup

### Dependencies

Some scripts like `./generate.sh` will download their own dependencies. However if you want to use this toolset it's a good idea to have these utilities installed:

- `jq`
- `yq` (the golang one, version 4+)
- `skopeo`
- `curl`

At the moment you will also need a `golang` development environment available.

The scripts are written on Linux for bash, so may not be POSIX compliant

### Create repo

Create a repo on GitHub, you probably want to name it similar to your operator, but it doesn't matter. For example, `rhbk-operator` has a FBC repo of `rhbk/rhbk-fbc`.

### Create initial config.yaml

In this git repo, the one source of truth is your `config.yaml`. Everything else is generated from this file using the scripts in this toolset. Here is an example config file:

```
name: rhbk-operator
repository: rhbk/keycloak-operator-bundle
konflux:
  namespace: rhbk-release
  prefix: rhbk-fbc
  github: rhbk/rhbk-fbc
ocp:
  - v4.13
  - v4.14
  - v4.15
replacements:
  - from: brew.registry.redhat.io/rh-osbs/keycloak-rhbk-rhel9-operator-bundle
    to: registry.redhat.io/rhbk/keycloak-operator-bundle
  - from: brew.registry.redhat.io/rh-osbs/keycloak-rhbk-rhel9-operator
    to: registry.redhat.io/rhbk/keycloak-rhel9-operator
  - from: brew.registry.redhat.io/rh-osbs/keycloak-rhbk-openshift-rhel9
    to: registry.redhat.io/rhbk/keycloak-rhel9
bundles:
  - sha256:c6a1b65abb5aa8fe301400790885e64592ef40b49364f305ad165cee87b0a60f
  - sha256:95af3ba537cf925f0359d54c7cd6d1dc360c9f109dcdd79322e9eb981c9b1ec6
  - sha256:47323bf5e0d1ec70bfec6d7dd476d1076d879d26cc166af451579e79a56046ec
  - sha256:5b6c852524af6ca1fbd6b8d76dba8c8ca55e160323c482d0cf1786db2b705d7d
  - sha256:dd2010b5aa0a8c8e0492b2f62c8d9a76466e972f33d4fa67a4535f711965d006
  - sha256:a47cee9b95ed78d7895c2582772abe3ccf239259ee3fbc2d7df8594450dc32f9
```

- `name` is the package name of your operator bundle.
- `repository` is the path of your bundle image repository within the Red Hat Container Ecosystem.
- The `konflux` section defines some key variables from the Konflux build system.
- `ocp` is the list of OpenShift versions you wish to support. You'll update this in response to OCP versions coming into and going out of support.
- `replacements` is required when you have internally images that are not yet accessible from their usual public place, it handles registry and path rewrites, but depends on digest pinning (don't use tags) for the images to work.
- Finally, the `bundles` section is a list of all the bundle images you want to include, across all channels and versions. The order doesn't matter. `bundles` is the part of the config file you will change most frequently.

There is a script to help you populate the bundles list, once you have the other sections in place. Run:

```
$ ./bootstrap-existing-bundles.sh
$ ./fix-bundle-mediatype.sh
```

`bootstrap-existing-bundles.sh` fetches the digests of all bundles you currently have published. `fix-bundle-mediatype.sh` is needed to ensure OLM reacts well in a multi-arch scenario when your bundle is only built for one architecture. This may change in the future if noarch bundles become available.

### Generate your FBC files

Run `./generate.sh` It does not take an parameters, and reads everything from `config.yaml`. It will download some tool binaries at specific versions that are known to work.

If you don't have authentication set up with `registry.redhat.io`, the script will prompt you to login first. Registry tokens can be obtained [here](https://source.redhat.com/groups/public/teamnado/wiki/brew_registry#obtaining-registry-tokens), and you can use them with the `podman login` command.

If you see the following message, your FBC has been created:

```
Catalog generated OK!
```

You can find the generated FBC files in the `catalog/` directory. You will need to commit these to your git repo. Don't hand-edit them.

### Onboard to Konflux

Follow Konflux's documentation to onboard your product and your new FBC. You will need one application perOCP version. Tell Konflux that it is a Dockerfile type application, with a root directory as one of the sub-directories in catalog/. Enable custom-pipeline and merge the PR Konflux creates. Things will probably not work initially!

You must use this naming pattern:

Applications: `<product>-fbc-v<ocp version>`, ex: `rhbk-fbc-v4-14`

Components: `<product>-fbc-component-v<ocp version>` ex: `rhbk-fbc-component-v4-14`

### Fix the Konflux tekton files

Use `./fix-tekton.sh` to change the files that Konflux generated to make them more appropriate for an FBC.

### Fix the Konflux config

Use `./fix-konflux-config.sh` to rewrite the automatically generated config objects within Konflux's OpenShift environment to better suit an FBC. This script will setup some dependency tools, including something that will authenticate the `kubectl` CLI through your browser, using your access.redhat.com credentials.

### ???

This is the part where you'll need to chase down bugs until all of your Konflux components build and test green! Try to contribute back any fixes to this tool repo, to help other products out.

### The fragment index images

The output of your Konflux build will be in quay.io. Each image contains a catalog fragment that you can use to test, similar to how IIB images are used.

The script `get-fbc-images-for-pr.sh` can help you to get the image coordinates list for a particular PR.

Note the index images will expire in 14 days unless bumped by updating the PR.

### Verifying the catalog

`./verify-catalog.sh` does all the checks it can, short of actually using your catalog within OpenShift. Mostly it will check that all images mentioned in the catalog actually exist.

If you've included non-public bundles, the test will fail, but it should report that it was able to find them in Brew.

A cache of existing images (`verified_coordinates`) is used to keep the execution time down for large catalogs. Don't commit this file to git if you happen to run the script locally.

It is a good idea to setup a github workflow to test each commit with this script. You also probably want to configure GitHub to make this check block the merge of a PR.

## Updating and releasing the catalog

Konflux generally works best if you use this update workflow:

1. File a PR for each change. Add your new bundle digest, run generate.sh, and then commit
2. Test that in OpenShift using an `ImageContentSourcePolicy` and `CatalogSource` to make the fragment index image
3. Ship the new bundle and other associated images
4. Merge the PR
5. Ensure the build goes ok
6. Create a release object in Konflux as defined in the konflux docs, reusing the same snapshot

`konflux-manual-release.sh` can help you to create release objects that are appropriate for a particular commit ID in your git repo (typically the ID of the merge commit you made when you merged the PR).

IIB is employed by Konflux after you release to merge the fragment catalog data into the single global Catalog for OpenShift/OLM.

## What is an FBC?

A FBC is a YAML or JSON file. A FBC's primary content is operator upgrade metadata. It defines the graph between each of your operator bundles, which can be anything you want. Many operators used to define this graph by the cumbersome `spec.replaces` entry in the bundle CSV YAML. This toolset assumes you want uncomplicated semantic versioning, without the need to manually define these relationships yourself!

In OLM parlance FBC is "a catalog", but you will manage only a fragment of the larger global catalog (the Catalog) that is used by OLM. A catalog is only valid for one version of OpenShift, so you'll probably need multiple FBCs in your FBC git repo, which likely will be identical unless you need to vary your upgrade graph per OCP version.

An FBC is also a container image. This is its form after it has been built. As of writing, the FBC image does contain some binaries. These are inherited from a parent image, that serve the FBC content via gRPC when executed. In the future binaryless FBC images may become the norm, and then they'll be more like how the bundle images are today.

The FBC does not replace your bundle images. It must be used inconjuction with valid images for operator, operand, and bundle. However, once you have a FBC set up, you can drop upgrade data like `spec.replaces` from your bundles.

Since the FBC exists seperately and asynchronously from your bundles, it can be used to rewrite history if you made a mistake a few releases back!

For more information see [the OLM Docs](https://olm.operatorframework.io/docs/reference/file-based-catalogs/).
