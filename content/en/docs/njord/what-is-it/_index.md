---
title: What is it?
description: Publish where you want (and more)!
categories: [Documentation]
tags: [docs]
projects: [ Njord ]
weight: 10
---

Njord is a Maven 3 and Maven 4 extension that offers **local staging, repository operations and repository publishing** and a `njord-maven-plugin` optional plugin. 
More precisely, Njord is a Resolver 1.x and 2.x extension (is [`RepositoryConnector`](https://github.com/apache/maven-resolver/blob/fb6e59027cfce9c9fce6f4e4f6d310c1a7ee906c/maven-resolver-spi/src/main/java/org/eclipse/aether/spi/connector/RepositoryConnector.java)) 
that is loaded via Maven extensions mechanism and extends Resolver. Njord does not mingle with your build at all.

Njord supports "templates", that define repository properties. Based on template, a local staging repository ("artifact store" in
Njord lingo) is created. And those local staging repositories can be merged, redeployed, dropped, validated or published (and 
more coming) through a Maven plugin. Also, based on chosen template, Resolver is configured to create mandatory checksums for you. On the
other hand, mandatory *signatures* are NOT generated, it is you who must provide them as part of your build.

In short, Njord keeps things "as before" (as without it): user never had to worry about checksums (Resolver did generate 
them always), while the signatures are usually provided by a plugin enabled in "release profile". Njord goes step 
forward, and IF user selects any "SCA" template  
("SCA" stands for "Stronger Checksum Algorithms", see [Resolver Checksums](https://maven.apache.org/resolver/about-checksums.html))
it will configure Resolver, and it will implicitly generate required stronger checksums without any user intervention required.

For now, templates supported out of the box are:

| Name                   | Mode       | Checksums Created                    | Signature Checked           | Redeploy allowed? |
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
* `njord:` - means "use default template (that is `release-sca`) and create a new store".
* `njord:snapshot` - means "use template by name `snapshot` and create a new store".
* `njord:store:release-00001` - means "select existing store `release-00001` and use that".

Basically by setting up your POM with distribution release repository using URL `njord:` and snapshot repository 
using URL `njord:snapshot` you are ready to use Njord. But, Njord is not intrusive, you can still use it by
**doing nothing** in your project and just deploying with `-DaltDeploymentRepository=id::njord:` as well.

Hints:
* use `mvn njord:list` to list existing stores, see [list Mojo](../plugin-documentation/list-mojo.html)
* use `mvn njord:list-templates` to list existing templates, see  [list-templates Mojo](../plugin-documentation/list-templates-mojo.html)

## The `njord` base directory

By default, Njord uses user-wide base directory (`~/.njord/njord.properties`). This is where Njord global
configuration and also staged contents are.

This directory is not bound to any project, hence, you are free to go to one project, stage it locally, then
go over another project, and stage that one as well, and so on.

Moreover, many Njord plugin mojos does not require project, hence you can operate on staged contents outside
of any project. Projects merely serve as "configuration source", but you can always publish a staged store
from outside it, by properly configuring `publish` mojo.

## The `njord` bundles

Njord by default produces two kinds of "bundles". They are very similar, as essentially both are ZIP files
with contents being artifacts laid down on Maven layout. But, there are subtle differences between the two:

The Mojo `write-bundle` will write out **"bundle"** file, that is a ZIP file and it will contain only the artifacts
laid down on Maven layout. This is the same file format used for publishing for example on Maven Central.

The Mojo `export` will write out **"transportable bundle"** (NTB, "Njord Transportable Bundle"), that is very similar 
to "bundle", but contains also Njord metadata, and can be imported by Njord too. This means you can carry staged content from
one workstation to another workstation, like it was locally staged on another workstation. Export and Import combined
with "install" publisher (that installs into local repository) can be also used in use cases like preparing some 
testing.

Differences are:

| Use case                                              | **bundle** ZIP | **transportable bundle** ZIP                            |
|-------------------------------------------------------|----------------|---------------------------------------------------------|
| Can be published to Maven Central Portal              | Yes            | No (probably, unsure whar will Portal do with metadata) |
| Can be imported on another workstation                | No             | Yes                                                     |
| Can be "mounted" as Remote Repository by Resolver 2.x | Yes            | Yes                                                     |
| Can be "overlaid" by Mimir                            | Yes            | Yes                                                     |

Notes:
* Resolver 2.x `file` transport supports `bundle:" protocol, see [here](https://github.com/apache/maven-resolver/tree/master/maven-resolver-transport-file).
* Mimir supports "overlay" functionality, where it is able to overlay ZIP content over contents of remote repository caches, see this [Mimir IT](https://github.com/maveniverse/mimir/tree/main/it/extension-its/src/it/overlay).

## The `njord` attachments

Njord is able to add "attachments" to bundles. Those are opaque file-like contents added to stores.
Store attachments are handled with following Mojos:

* `attachment-from-tile` adds store attachment from file user points at
* `attachment-to-file` writes out store attachment to the file user points at
* `attachment-delete` deletes a store attachment
* `attachment-list` lists all store attachments

Attachments are meant to carry some "orthogonal" information to store (artifacts), like some metadata collected
during the build and similar. Attachments may be handled by publisher, if it wants to. Currently no publisher
handles attachments.

Hence, attachments are simply lost, for example when using `sonatype-cp` publisher, or when exporting
store as "bundle". It is only the "transportable bundle" that carries over attachments.
