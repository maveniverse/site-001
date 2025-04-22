---
title: What is it?
description: Publish where you want (and more)!
categories: [Njord, Documentation]
tags: [njord, docs]
weight: 10
---

Njord is a Maven 3 and Maven 4 extension that offers local staging, repository operations and repository publishing. 
More precisely, Njord is a Resolver 1.x and 2.x extension (is yet another [`RepositoryConnector`](https://github.com/apache/maven-resolver/blob/fb6e59027cfce9c9fce6f4e4f6d310c1a7ee906c/maven-resolver-spi/src/main/java/org/eclipse/aether/spi/connector/RepositoryConnector.java)) 
that is loaded via Maven extensions mechanism and extends Resolver. Njord does not mingle with your build at all.

Njord supports "templates", that define repository properties. Based on template a repository ("artifact store" in
Njord lingo) is created. And those repositories can be merged, redeployed, dropped, validated or published (and 
more coming).

For now, templates supported out of the box are:

| Name                   | Mode       | Mandatory Checksums                  | Mandatory Signatures        | Redeploy allowed? |
|------------------------|------------|--------------------------------------|-----------------------------|-------------------|
| `release`              | `RELEASE`  | `SHA-1`, `MD5`                       | `GPG` (`Sigstore` optional) | no                |
| `release-sca`          | `RELEASE`  | `SHA-512`, `SHA-256`, `SHA-1`, `MD5` | `GPG` (`Sigstore` optional) | no                |
| `release-redeploy`     | `RELEASE`  | `SHA-1`, `MD5`                       | `GPG` (`Sigstore` optional) | yes               |
| `release-redeploy-sca` | `RELEASE`  | `SHA-512`, `SHA-256`, `SHA-1`, `MD5` | `GPG` (`Sigstore` optional) | yes               |
| `snapshot`             | `SNAPSHOT` | `SHA-1`, `MD5`                       | `GPG` (`Sigstore` optional) | no                |
| `snapshot-sca`         | `SNAPSHOT` | `SHA-512`, `SHA-256`, `SHA-1`, `MD5` | `GPG` (`Sigstore` optional) | no                |

To deploy to Njord repository, one can use the usual Resolve remote repository URL with protocol `njord:`.
The examples below with the `id::` prefix (repository ID) can be used by `maven-deploy-plugin` for 
`-DaltDeploymentReposiotory`, but in this case the `id` is really just a placeholder to fulfil the required
syntax.

Example URIs:
* `njord:` - means "use default template and create a new store" that is `release-sca`.
* `njord:snapshot` - means "use template by that name and create a new store", in this case `snapshot`
* `njord:store:release-00001` - means "select existing store release-00001 and use that", in this case store `release-00001`.

Basically by setting up your POM with distribution release repository using URL `njord:` and snapshot repository 
using URL `njord:snapshot` you are ready to use Njord. But, Njord is not intrusive, you can still use it by
**doing nothing** in your project and just deploying with `-DaltDeploymentRepository=id::njord:` as well.
