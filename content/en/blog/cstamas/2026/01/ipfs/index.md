---
title: "Maven @ IPFS"
date: 2026-01-22T10:55:53+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - maven
  - ipfs
projects:
  - Maven
---

Lately has been toying with IPFS to achieve content sharing without centralized infrastructure. In other words, instead
to free-ride on some (centralized) infrastructure that may be a public good, or some commercial offering, solve the publishing
(and also "owning" and "hosting" the data) by my self. Kinda reminded me this to early 2000s, when many ran 
Maven repositories in their own basements, making access to their repositories fragile, with longevity accessibility
and uptimes totally unpredictable. That was before Central, which consolidated but also promoted itself as single point of
failure. And hence, ended up as over- and misused, see [Maven Central and the Tragedy of the Commons](https://www.sonatype.com/blog/maven-central-and-the-tragedy-of-the-commons).

Hence, I wanted plan B for our Maveniverse organization. What if we -- aside of continued publishing to Central -- offer
other ways to get artifacts for those interested in them, let them keep them in a way they want (not possible with Central,
mirroring is still not an option), and have them full access to artifacts (ie indexing, scanning, whatever)?

## Enter IPFS

I will not spend a lot on explaining IPFS, it has a nice [documentation available already](https://docs.ipfs.tech/).
If anything else, at least read [this page](https://docs.ipfs.tech/concepts/ipfs-solves/).

In short, IPFS is a decentralized network, running IPFS nodes and implementing Content Addressable Storage (CAS) and
more. Terms worth knowing about are [CID](https://docs.ipfs.tech/concepts/content-addressing/#what-is-a-cid), 
that in very simplified form, can be understood as a "hash" (content solely content hash), pointing to some
content (any content). The content behind CID can be one of multiple things (but once set, is immutable): it can
point to contents of a JAR file, or in fact any file, but it can be a DAG backed by IPLD schema [file system](https://docs.ipfs.tech/concepts/file-systems/).
This means that CID may point even to "file hierarchy", like on Linux systems, with directories and files and everything.
These structures are colloquially called "Merkle Trees", and are built "bottom up", from leaves (files) toward root.
Hence, in case of change (ie another file added to a directory), the existing file CID remains unchanged, but due their
shared parent directory changed, its CID and root CID will change.
Producing CID is free to everyone: just run an IPFS node and upload some content to it, and you will get a CID for it.
Important thing to consider, is that if two persons, independently, upload some content and both end up with same CID
(with some fine print, later about that), it means they both independently published bit-by-bit _same content_ (IPFS is 
content addressable).

Having the CID is like having the "address", but where is the content behind the address? For start, it is in the node
you uploaded the content to get the CID. With "pinning", you can make your node pull down any CID backing content
(assuming is reachable). Basically you maintain your node, letting it stick to content you want/need, and merely
caching the rest (IPFS node storage performs regular garbage collections, dropping unreachable or stale content). Furthermore,
there are (paid or free) services for "pinning content", by using those services, you can make sure content is "pinned"
and swiftly served to any node wanting it. But this is out of scope for this article.

Another term is [IPNS](https://docs.ipfs.tech/concepts/ipns/), that is like "mutable CID" (maybe consider it like DNS). For creating IPNS entries
a private cryptographical key is required, and each key can produce _one IPNS entry_. At the same time, one node (or user)
can mangle as many keys as they want. And this is important thing: as I explained above, anyone can create CID, but if
consumer asks IPNS "which is CID you published", all user has to do is resolve IPNS to get the right CID, as IPNS
entry is the function of private key, and it cannot be faked. Nor CID or IPNS is "human friendly", kinda, but there
are solutions to it like [DNSLink](https://dnslink.dev/) where IPNS can be exposed via DNS and "human friendly" domain.

{{% pageinfo color="info" %}}

Have to note several key things to reassure IPFS users: 
* IPFS works in similar fashion as Torrent, uses DHT and various other means to let nodes discover each other. In short, 
  the more nodes the merrier. In other words, "popular" content may be cached on multiple nodes, and hence, will be 
  faster getting them.
* Each IPFS node participates in traffic direction (ie passing messages) among each other, telling about discovered nodes, 
  and offering local content, if asked for.
* Important thing to note, is that if you run your node **it will store only the content you tell it to store** 
  (by locally pushing or pinning), it will NOT store random content from internet.
* There is pretty much nothing needed on your side (network setup or alike) to make IPFS published. 

{{% /pageinfo %}}

## Rounding it up

So what gives this?
* CID points to content/structure and is immutable (same CID will always return same content, if content is accessible)
* IPNS points to "up to date" CID, and you can be sure entry was published by key owner only and nobody else
* DNS points to IPNS, and again, assuming you trust the domain owner, you can then delegate your trust to IPNS entry it points to. This trust delegation 
  is very similar to Central, where you need to provide proof to get publishing namespace (that is ideally a reverse domain).

In short, we have a series of indirection: `domain -> IPNS -> CID`. If you get to CID by hopping over these stops, all 
fine. But what happens if your private key (used for publishing IPNS) is compromised? Just create new key, republish the 
content with it, and update DNSLink for your domain (and of course, communicate it). After all, we still can GPG sign 
artifacts, so IPNS + GPG is good enough.

An example of this setup can be seen at [ipfs.maveniverse.eu](https://ipfs.maveniverse.eu/).

Details:
* the `ipfs.maveniverse.eu` domain uses DNSLink to publish TXT record with IPNS (try `dig _dnslink.ipfs.maveniverse.eu TXT`)
* the IPNS entry is in form of `/ipns/xxxxxxxxxx`
* the IPFS node can resolve `/ipns/xxxxx` address to `/ipfs/xxxxx` CID.

## Maven @ IPFS

Maven release repositories seems like perfect candidates to be put onto IPFS: they are immutable. Or to be more precise,
the leaves (artifacts) in a repository will remain immutable, and by deploying (more) only parent and paren parent changes,
in essence the root CID changes. Aside of parents, G and A level metadata changes as well, but those are not leaves.

Maveniverse [IPFS](https://github.com/maveniverse/ipfs) extension provides support for this setup above, and is even
usable on CI to consume (and later to deploy).

The extension requirements are Java 11+ and a reachable Kubo RPC API (simplest is to have it running on localhost) and
adds following components to Maven:
* adds IPFS transporter supporting `ipfs:/` URLs
* adds IPFS publishing support via lifecycle participant

The IPFS URL looks like `ipfs:/name[/subpath]` where parts are:
* protocol `ipfs:/` is fixed and must
* for consuming, the `name` element should be **resolvable**. It can be CID, IPNS or DNSLink-ed domain.
* for deploying, the `name` element aside of that above, should be the name of a **private key** present in IPFS node used to publish IPNS
* optional `/subpath` defines the path prefix within `name`

Have to mention, that if using CID for `name`, it is user responsibility to _ensure_ proper CID is used, since as explained
above, CIDs can be created by anyone, and it may contain fake or even malicious artifacts. When using IPNS record,
similar thing, user has to ensure that he resolves the proper IPNS (but if trust is established, all is good). Finally,
in case of using (IPFS resolvable) domain, same level of trust can be established as in case of Central, one can
safely assume that domain owner publishes right thing (same as on Central).

A little bit of digression here: in case `name` is a domain, I was tinkering to **limit** Maven @ IPFS to get only artifacts
from domains namespace, for example `maveniverse.eu` should offer **only `eu.maveniverse` namespace**. Any ideas welcome!

{{% pageinfo color="info" %}}

Important: the current workflow Maven @ IPFS implements works of small scale, ie Maveniverse forge level, that has handful
of Megabytes of artifacts. The current workflow due refresh/pinning (downloading whole blob) does not scale, but works
pretty nicely on small scale.

{{% /pageinfo %}}

## Mimir @ IPFS

As mentioned above, in repositories published with Maven @ IPFS, the _leaves will not change_. That means that their 
CID remains unchanged. Next level would be _IPFS global caching_, for example with Mimir (that already offers similar
service on LAN using JGroups). Here, some translation needs to be done, that begins with GAV and ends with CID.

## Final thoughts

I am not planning to pull back Maven publishing back to "stone age" (the 2000s, with many little repositories coming and 
going), but IPFS definitely has merit in several use cases. Some of them, just without any ordering are:
* publishing snapshots across (probably totally disconnected) CI jobs
* any ad-hoc kind of publishing without infrastructure
* small scale forges

But I personally think that (global) caching w/ Mimir may be very interesting.

Once something more in place, will report back! Cheers and have fun!