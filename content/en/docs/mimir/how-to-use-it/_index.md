---
title: How to use it?
description: The Maven workstation and LAN cache
categories: [Documentation]
tags: [docs]
projects: [ Mimir ]
weight: 30
---

Simplest way to use Mímir is with Maven 4, it supports **user wide extensions**. Just create `~/.m2/extensions.xml` 
with following content (adjust Mímir version as needed):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<extensions>
    <extension>
        <groupId>eu.maveniverse.maven.mimir</groupId>
        <artifactId>extension3</artifactId>
        <version>${mimirVersion}</version>
    </extension>
</extensions>
```

You can add it to your (parent) POM as well, as build extension:

```xml
    <extensions>
      <extension>
        <groupId>eu.maveniverse.maven.mimir</groupId>
        <artifactId>extension3</artifactId>
        <version>${mimirVersion}</version>
      </extension>
    </extensions>
```

Using it with Maven 3 is also possible and completely fine and compatible, but there you will need to set up
per-project extensions in `.mvn/extensions.xml` file instead of one user-wide one.

One extra step is needed, in case you have non-trivial networking (like Docker, Tailscale or alike): you need 
to "help" Mimir a bit to figure out which networking interface belongs to your LAN. To achieve that,
you need to create `~/.mimir/daemon.properties` file with following content (use your LAN IP address):

```properties
mimir.localHostHint=match-address\:192.168.1.*
```

This will help JGroups and Mimir system node publishers to properly bind to interface that is used on your LAN.

{{% alert title=Note color=info %}}

On hosts where there is running Docker, Tailscale etc. it may be impossible to "figure out"
which interface and which address correspond to LAN address, if any. Hence, one can give Mimir a "hint" that is
globally applied at Mimir level (like publishers or LAN sharing is). Accepted hints are:

* `match-interface:value`
* `match-address:value`

In both cases "value" may end with "*" (asterisk). If no asterisk, value equality is checked, if it ends with
asterisk, then "starts with value" is checked.

Examples: `match-interface:enp*` (means "use interface whose name starts with enp") or `match-address:192.168.1.10` (means "use address that equals to 192.168.1.10")

These hints may still produce wrong address selection, so one should check logs to ensure about them.

For the full documentation of `mimir.localHostHint` configuration is in Javadoc.

{{% /alert %}}


With these, you are fully set up. Now just go and fire up a Maven or Maven Daemon build.