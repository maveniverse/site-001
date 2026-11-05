---
title: Checksum Suite
description: Checksums powers to Maven!
categories: [Documentation]
tags: [docs]
projects: [ Checksum ]
weight: 170
---

{{% pageinfo %}}
Checksum Suite empowers Maven 3.9/Resolver 1.9 (and requires too at runtime) by adding a nearly trivial plugin
to perform usual "checksum related stuff", and an extension that provides modern cryptographically strong checksums.
{{% /pageinfo %}}

Since Maven 3.9 (Resolver 1.9) checksum algorithms are pluggable via an SPI, and SHA-256 and SHA-512 are supported
out of the box, but the defaults remained SHA-1 and MD5. Checksum Suite consists of a Maven plugin and a core
extension, both small and without dependencies, and usable independently of each other.

The plugin lists supported checksum algorithms and calculates checksums for any file or for project artifacts,
without changing Maven or Resolver configuration. The original motivation was the ASF release process, where all
artifacts use the default checksums, but the source release ZIP needs a SHA-512 one.

The extension hooks into the Resolver checksum SPI and exposes every `MessageDigest` algorithm available in the JVM
as a checksum algorithm, so newer ones like SHA-3 variants become usable. Optionally it registers the BouncyCastle
provider as well, making algorithms like BLAKE2 available.

Sources: https://github.com/maveniverse/checksum

[Maven generated plugin documentation](plugin-documentation/plugin-info.html)
