---
title: Maven@IPFS
description: Maven suite to use IPFS
categories: [Documentation]
tags: [docs]
projects: [ IPFS ]
weight: 130
---

{{% pageinfo %}}
Maven suite to use IPFS.
{{% /pageinfo %}}

Maven@IPFS is a core extension that adds an [IPFS](https://ipfs.tech/) transport to Maven Resolver. With it loaded,
remote repositories can be declared with URLs of the form `ipfs:/name[/subpath]`, where `name` is a CID or any
IPNS-resolvable name (a key hash or a DNSLink-enabled domain).

The transport talks to an IPFS node, by default one running on localhost (for example IPFS Desktop). Consuming
requires nothing more than a running node. Deploying requires the node to have a key with the same name as used in
the repository URL; publishing under that name is only possible with the private key, while DNSLink gives a
human-friendly `domain -> IPNS -> CID` indirection.

The same content is also reachable via public IPFS HTTP gateways using the plain HTTP transport, but running an own
node is recommended. Requires Java 11+ and Maven 3.9+.

Sources: https://github.com/maveniverse/ipfs
