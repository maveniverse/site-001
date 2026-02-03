---
title: "Maven @ IPFS (II)"
date: 2026-02-03T11:55:53+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - ipfs
  - cache
  - publish
projects:
  - Maven
---

{{% pageinfo color="info" %}}

Lately has been toying with IPFS to achieve content sharing without centralized infrastructure. In other words, instead
to free-ride on some (centralized) infrastructure that may be a public good, or some commercial offering, solve the publishing
(and also "owning" and "hosting" the data) by my self.

This entry explains the simplest use case: "small scale publishing". Other use cases are "global caching" and will
work them out later.

{{% /pageinfo %}}

## Let's dream together!

As I mentioned previously, it is colloquially said that "IPFS is like BitTorrent": the more, the merrier. So, imagine
if every Maven user would automatically run an IPFS node as well. Also, imagine if publishers would make sure that
their content is always available (for this you need persistently running IPFS nodes, not ad-hoc nodes that run on
your laptop), but is doable in many other ways as well.

Of course, this is not happening today, so in my Maven related experiments I target smallest scale first.

## Small Scale Publishing

I also call this use case "ad-hoc publishing" or just "transient snapshot sharing". And all this is doable without 
server infrastructure. Also, this is the simplest use case for IPFS.

Here, the **assumption is that the dataset you publish/own/govern is relatively small**, like one namespace, or just 
current snapshots of a project or alike. This use case is already supported by [Maveniverse IPFS](https://github.com/maveniverse/ipfs).
The point of this use case, is that it allows quick turnaround without any requirement of server infrastructure setup,
and works across nodes (even on CI servers like GitHub Actions).

In this case, publisher publishes complete Merkle Tree (hence the size constraint), and consumer consumes it. It has to 
be noted, that due Merkle Tree nature, leaves of the tree (the artifacts themselves) are immutable. Hence, leaves will 
keep their CID upon continued publishing (like of a new version), nodes "toward the root" of the tree, where the CID is 
changing. The IPNS that is regularly updated, always points to latest root CID. This is true for Maven release artifacts, that are by
definition immutable. For snapshots (also immutable since Maven 3.0!), we can adopt various strategies, and given they need cleanup anyway, maybe the
simplest is just to always create "new repo" and just toss the "old repo" into oblivion.

To use this extension, one must have a locally running IPFS node (Kubo) as the extension interacts with
Kubo node via RPC API, and this RPC must not be exposed to public internet. For consumers, the simplest is to install [IPFS Desktop](https://docs.ipfs.tech/install/ipfs-desktop/)
application and run it when needed. That's it! To disperse possible concerns, these things you need to know about IPFS:
* IPFS Desktop is an integrated solution with GUI and background running Kubo IPFS daemon.
* By default, IPFS node will consume most of 10GB of disk space (it starts empty).
* Every IPFS node takes part in "routing", but it does not involve any content passing.
* Your IPFS **node will store only content you ask for**. So, don't be worried, you are not forced to store any unwanted content.
* Content from storage is GC-ed from time to time. To make content persistently stored (in your node), you need to "pin" it.
* Content is "available" only if there is reachable node offering it, hence publishers want long-running IPFS nodes.
* IPFS offers various persistent storage options, that I am not discussing it here.

### Publisher workflow

Publisher is the source of Artifacts, and is offering them for consumption. Publisher in this example performs following
actions:
* run an IPFS node, make sure content is persistently available (pinned), and that the node(s) offering the content are 24/7 available
* ideally, provides a "human friendly" entrypoint, like a domain is that points to IPNS entry
* keeps hold on private key used to create IPNS entry
* produces and publishes artifacts to IPFS

Let's see an example! In this example I will use Maveniverse own IPFS content.

The domain for humans is [ipfs.maveniverse.eu](https://ipfs.maveniverse.eu/), which is DNSLink-ed to private key I use to publish to this namespace:
```
$ dig _dnslink.ipfs.maveniverse.eu TXT
...
;; ANSWER SECTION:
_dnslink.ipfs.maveniverse.eu. 3600 IN	TXT	"dnslink=/ipns/k51qzi5uqu5dji6oq9whgjw8c8mkmv45a2ros93ncnluae37i2ayef5cscdoqu"
...
```

With this IPNS record, once can already inspect content (CID it points to, and content backing the CID) by using one
of the public HTTP Gateways of IPFS: [http://ipfs.io/ipns/k51qzi5uqu5dji6oq9whgjw8c8mkmv45a2ros93ncnluae37i2ayef5cscdoqu](http://ipfs.io/ipns/k51qzi5uqu5dji6oq9whgjw8c8mkmv45a2ros93ncnluae37i2ayef5cscdoqu).
Behind the scenes, the Gateway resolve the IPNS record (that is hash of the private key) to a CID, and renders the
content behind it (it is backed by Merkle Tree, so we should see directories).

Publisher, with this one time setup (domain and private key in IPFS node) is ready to publish using Maven. To achieve this,
publisher needs to:
* run an IPFS node
* load Maveniverse IPFS extension
* define distMgt namespace
* publish/deploy as usual

Once IPFS node is up and running, lets move to Maven side of things.
To load the extension, one need to create project-wide (or user-wide with Maven 4) `extensions.xml` with following content:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<extensions>
    <extension>
        <groupId>eu.maveniverse.maven.ipfs</groupId>
        <artifactId>extension3</artifactId>
        <version>$VERSION</version> <!-- Currently is 0.3.0 -->
    </extension>
</extensions>
```

This will early load the IPFS extension into Maven and make it available. Next, as usual, in POM one need to define
the remote repository:
```xml
  <distributionManagement>
    <repository>
      <id>maveniverse-releases</id>
      <url>ipfs:/ipfs.maveniverse.eu/releases</url>
    </repository>
</distributionManagement>
```

And just deploy/publish (using deploy publisher) as usual. Publisher may sense slight delay at session beginning and
at session end. This is what happens behind the curtain:
* namespace (in this case `ipfs.maveniverse.eu`) is being resolved (DNS -> IPNS -> latest CID)
* the CID is being (lazy) copied to local node MFS and then pinned
* IPFS transport in Maven deploys to MFS as usual
* on session end, the updated namespace is being published to IPNS using designated private key (recommended settings for publishers for Kubo: "Enable IPNS over PubSub")
* (optional) "seed" the content to multiple IPFS nodes, for example in my case, from my IPFS Desktop I seed two persistent nodes: one in HU and one in DK (this step is not automated).

### Consumer workflow

Consumer is consuming artifacts published by one or more publishers. For this to happen, consumer need to do following
actions:
* run an IPFS node
* load Maveniverse IPFS extension
* define consumed namespace or namespaces
* use Maven as usual

Let's see an example! In this example I will use Maveniverse own IPFS content. Have your IPFS node running!

Once IPFS node is up and running, lets move to Maven side of things.
To load the extension, one need to create project-wide (or user-wide with Maven 4) `extensions.xml` with following content:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<extensions>
    <extension>
        <groupId>eu.maveniverse.maven.ipfs</groupId>
        <artifactId>extension3</artifactId>
        <version>$VERSION</version> <!-- Currently is 0.3.0 -->
    </extension>
</extensions>
```

This will early load the IPFS extension into Maven and make it available. Next, as usual, in POM one need to define
the remote repository:
```xml
    <repository>
      <id>maveniverse-releases</id>
      <url>ipfs:/ipfs.maveniverse.eu/releases</url>
    </repository>
```

And just build "as usual", artifacts from Maveniverse namespace will be available to you. Consumer may sense slight delay 
at session beginning. This is what happens behind the curtain:
* namespace (in this case `ipfs.maveniverse.eu`) is being resolved (DNS -> IPNS -> latest CID)
* the CID is being (lazy) copied to local node MFS (optionally pinned)
* IPFS transport in Maven consumes from MFS as usual

## Conclusion

The extension introduces three set of components:
* IPFS core components (that talk to IPFS node)
* Maven Lifecycle Participant, that triggers publishing, if needed
* IPFS transport for Resolver

The transport uses URI of format `ipfs:/namespace[/suffix]`. It is expected that `namespace` is resolvable with IPFS
node, so it can be:
* DNSLinked domain (similar trust model as in Central)
* IPNS hash, like `k51qzi5uqu5dji6oq9whgjw8c8mkmv45a2ros93ncnluae37i2ayef5cscdoqu` (in this case user would want to make sure that IPNS record comes from one he thinks should come)
* IPFS CID, like `Qmf7tb4UEJwyCrf6FzjmMTLxJgQuqd7RBGk14JEK5GhYGf` (in this case user would **really want to make sure CID content is what he expects**; there is no trust in this)

The `suffix` is optional, and is really like a path, that may point inside the Merkle Tree, like in example of Maveniverse
IPFS where root contains multiple repositories.

For publishers, simplest is to create named private key **have same name as namespace**, as that makes administration
simplest. In case of having multiple publishers for one namespace (like we do in Maveniverse), it is enough to share
private key via same sane (and secure) means, and whoever has private key can publish to namespace. If private key
is compromised (or just as part of maintenance), old private key can be tossed and new generated. This step requires
DNS Link update (as IPNS record changed due new private key). And that's it.

```
$ ipfs key list -l
k51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx self
k51qzi5uqu5dji6oq9whgjw8c8mkmv45a2ros93ncnluae37i2ayef5cscdoqu ipfs.maveniverse.eu 
$ 
```

This, as already said, is the simplest use case, usable for small scale publishing, as MFS is being involved in the process.
But, have to emphasize, that artifact CIDs produced in this way, will become usable in other use cases, like 
"global caching" too.