---
title: What is it?
description: Publish where you want (and more)!
categories: [Njord, Documentation]
tags: [njord, docs]
weight: 10
---

Njord is a Maven 3 and Maven 4 extension that offers **local staging, repository operations and repository publishing**. 
More precisely, Njord is a Resolver 1.x and 2.x extension (is [`RepositoryConnector`](https://github.com/apache/maven-resolver/blob/fb6e59027cfce9c9fce6f4e4f6d310c1a7ee906c/maven-resolver-spi/src/main/java/org/eclipse/aether/spi/connector/RepositoryConnector.java)) 
that is loaded via Maven extensions mechanism and extends Resolver. Njord does not mingle with your build at all.

Njord supports "templates", that define repository properties. Based on template a repository ("artifact store" in
Njord lingo) is created. And those repositories can be merged, redeployed, dropped, validated or published (and 
more coming). Also, based on chosen template, Resolver is configured to deploy mandatory checksums for you. On the
other hand, mandatory signatures are NOT generated, it is you who must provide them as part of your build.

In short, Njord keeps things "as before" (as without it): user never had to worry about checksums (Resolver did generate 
them always), while the signatures are usually provided by a plugin enabled in "release profile". Njord goes step 
forward, and IF user selects any "SCA" template  
("SCA" stands for "Stronger Checksum Algorithms", see [Resolver Checksums](https://maven.apache.org/resolver/about-checksums.html))
it will configure Resolver, and it will implicitly generate required stronger checksums without any user intervention required.

For now, templates supported out of the box are:

| Name                   | Mode       | Mandatory Checksums                  | Mandatory                   | Redeploy allowed? |
|------------------------|------------|--------------------------------------|-----------------------------|-------------------|
| `release`              | `RELEASE`  | `SHA-1`, `MD5`                       | `GPG` (`Sigstore` optional) | no                |
| `release-sca`          | `RELEASE`  | `SHA-512`, `SHA-256`, `SHA-1`, `MD5` | `GPG` (`Sigstore` optional) | no                |
| `release-redeploy`     | `RELEASE`  | `SHA-1`, `MD5`                       | `GPG` (`Sigstore` optional) | yes               |
| `release-redeploy-sca` | `RELEASE`  | `SHA-512`, `SHA-256`, `SHA-1`, `MD5` | `GPG` (`Sigstore` optional) | yes               |
| `snapshot`             | `SNAPSHOT` | `SHA-1`, `MD5`                       | `GPG` (`Sigstore` optional) | no                |
| `snapshot-sca`         | `SNAPSHOT` | `SHA-512`, `SHA-256`, `SHA-1`, `MD5` | `GPG` (`Sigstore` optional) | no                |

## The `njord:` URI

Njord can be considered also as new transport for Maven. It defines the `njord:` URI prefix and supports several
forms:
* `njord:` URI is a shorthand for `njord:release-sca` (default template), see below.
* `njord:<TEMPLATE>` is equivalent to `njord:template:<TEMPLATE>`, see below.
* `njord:template:<TEMPLATE>` URI when deployed to, will create new store using given template.
* `njord:store:<STORE>` URI when deployed to, will try to deploy to given store that already must exist (will not be created).

Similarly, to use Njord URIs in cases like `maven-deploy-plugin` parameter for alternate deployment repository, the format
accepts `id::uri` formatted string, so Njord URIs looks like `id::njord:` or `id::njord:template:release-sca` with one 
important detail: the `id` repository ID is there **only to fulfil syntactical requirements**, is unused otherwise. 
Store name will be determined at the moment of creation.

Example URIs:
* `njord:` - means "use default template and create a new store" that is `release-sca`.
* `njord:snapshot` - means "use template by name `snapshot` and create a new store".
* `njord:store:release-00001` - means "select existing store `release-00001` and use that".

Basically by setting up your POM with distribution release repository using URL `njord:` and snapshot repository 
using URL `njord:snapshot` you are ready to use Njord. But, Njord is not intrusive, you can still use it by
**doing nothing** in your project and just deploying with `-DaltDeploymentRepository=id::njord:` as well.

Hints:
* use `mvn njord:list` to list existing stores, see [list Mojo](../plugin-documentation/list-mojo.html)
* use `mvn njord:list-templates` to list existing templates, see  [list-templates Mojo](../plugin-documentation/list-templates-mojo.html)
