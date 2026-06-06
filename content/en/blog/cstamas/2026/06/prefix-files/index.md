---
title: "Prefix Files"
date: 2026-06-06T11:32:00+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - maven
  - resolver
projects:
  - Resolver
---

{{% pageinfo %}}

This post tries to explain a Maven repository feature existing since early 2010s, that is now with Resolver 2.x
becoming utilized even on Maven side for better security and performance.

{{% /pageinfo %}}

With Resolver 2.x being used in Maven 3.10.x and Maven 4.x lines (and finally, dropping legacy of Resolver 1.x),
users will hear more and more about [Remote Repository Filtering](https://maven.apache.org/resolver/remote-repository-filtering.html) (RRF).
The essence of RRF is manifold, and is explained on referenced page, and even a demo exist that demonstrates what RRF can
do, for example here: https://github.com/cstamas/rrf-demo

The Resolver RRF (by the way, existing in Resolver 1.9/Maven 3.9 line as well, but disabled by default) consists of
two filtering algorithms: "prefix" and "groupId", and the two combined has great powers to increase your build
security and speed. Important to note, that RRF is applied to Artifacts and Metadata only, is not applied to any
other resource in repository.

Still, one piece seems was not explained enough, as people are getting confused on it: the prefix files.

## Prefix files

The prefix file is a simple UTF-8 encoded text file with defined content, an expected magic as first line, and body. 
Resolver will accept only "well formatted" prefix files. The prefix file has nothing to do with Artifact or Metadata 
coordinates, or GAVs in general. They are about URI-like paths (path separator is always `/`). Line-endings are
laxed, in a way, they could be anything that Java recognizes as "line ending" (basically Unix/Windows, any will do,
Unix ones preferred due size).

Prefix file header/magic MUST be first line containing exactly this string: `## repository-prefixes/2.0`. If the file very
first line does not equals to this line, prefix file is rejected as "invalid".

The body follows after magic, and each line must be maximum 250 character long and must have maximum of 100000 lines.
If any of these are violated, prefix file is rejected as "invalid".

Body is parsed line by line, and each line can be one of these:
* exactly string `@ unsupported`, this string can occur at any line (even after many previous body lines, and causes prefix file to be rejected as "declares itself unsupported")
* an empty string (just a newline; for human formatting purposes) -- is ignored (block/formatting/separation within file)
* a string beginning with `#` character followed by any characters up to line ending (for human formatting purposes) -- is ignored (comment)
* a string starting with `/` (slash) and followed by some letters, containing a prefix in form of `/org/domain` (see below about "depth" of prefix)

Any violation of these, will again reject prefix files as "invalid".

A valid example of some imaginary (as example is incomplete) prefix file looks like this:

```text
## repository-prefixes/2.0

# our stuff
/eu/maveniverse

# ASF Maven stuff
/org/apache/maven
/org/codehaus/plexus

# some other stuff
/dev/jbang
```

But, prefix files are usually generated, and not authored by humans.

## Prefix file semantic

The lines in prefix file body represents "path prefixes from repository root" that exists in repository. As we talk about Artifacts
and Metadata, GAVs in both cases, their GAV applied onto remote repository [layout](https://maven.apache.org/repositories/layout.html)
ends up with a URI path. And this URI should have matching prefix enlisted prefixes in prefixes file, that means that
Artifact or Metadata "is allowed" from given remote repository. In other case, it is "filtered out".

This above have interesting consequences. Prefix file is just "best effort", as its selectivity can be "tuned".
The fact that prefix `/org/apache` is matched, it does not mean that GAV being matched is "for sure" present! GAV
could still point to some nonexistent artifact. Prefix file is also very useful to filter our "for sure not here"
cases, preventing doing requests to remote that are known that will end up as HTTP 404 or some protocol equivalent of "Not found".
In example above, asking for `com.google.inject:guice:6.0.0` is not even attempted, as imaginary prefix has no matching
prefix for this GAV.

Think for example about entry like `/com`, this says "I have some path that starts with `/com`" but usually no repository
has everything with this prefix. Unless we talk about Maven Central only, but even then, if you bring into context some
company that uses hosted repositories for internal development, and their artifacts are not public, the statement
above is immediately wrong again. Using longer prefixes improves prefix file selectivity (but also increases its size).

Most selective prefix file by definition is when it lists full file paths of all artifacts in it (and is updated in a 
moment new deploy happens). One can achieve it by doing `find . -type f -printf '/%P\n'` from repository root. Still,
if the repository is growing, or is already huge, when it reaches the 100000 entries (a limit for entries within prefix file),
this cannot be done anymore. You need to lower the file entry count, and you can do it by finding "common prefixes".

There is a balance between prefix file size (see limits above) and selectivity. Hence, the prefix body are 
usually paths prefixes having depth from 2 to 4 (count of path segments included). Prefix file entries are usually in 
form of `/eu/maveniverse` (shortest, domain NS), to somewhat longer like `/eu/maveniverse/maven/plugins`, as needed. 
Segment count can even be different on each file entry as for example in case of [Maven Central prefix file](https://repo.maven.apache.org/maven2/.meta/prefixes.txt).

On other end, the smallest valid prefix file looks like this:

```text
## repository-prefixes/2.0
```

And the file meaning is "I have nothing" (I am en empty repository).

It is important to note here, that if resolver receives (configured by user or discovered from remote) a valid prefix 
file, it will obey it. This implies, that if you managed somehow (or your remote repository) to provide valid, but 
incorrect (like incomplete or mixed up origins) prefix file, your resolver resolutions are at stake.

## Prefix files application

Prefix files are usually published by repositories, and doing this is win-win for both parties:
* remote repository does not have to handle "known to not be there" requests (spending cycles on emitting 404s)
* resolver side can stop issuing "known to not be there" remote requests, making resolution faster 

Of course, users can also manually provide prefixes file, if needed.

Prefix file is applied onto remote repository, if all these conditions are true:
* prefix file content is made available. It means that prefix file was discovered by resolver (fetched from remote), or was provided by user. For example, if remote repository returns HTTP 404 for it, or user provided file is not found, it is not available.
* available prefix file is parsed, and was found valid. If parsing of prefix file did not result in rejection of being "invalid", it is considered valid.

Prefix files are by definition located as plain text files on remote repository at repository path of `.meta/prefixes.txt`.
This means, that for example Maven Central published prefixes file is available from the following URL:
https://repo.maven.apache.org/maven2/.meta/prefixes.txt

## Controlling prefix filter

Check out [Resolver configuration](https://maven.apache.org/resolver/configuration.html) and you will find several
configuration keys with prefix (heh) of `aether.remoteRepositoryFilter.prefixes...`. Note, many keys supports RepoID suffix,
that means that configuration key appended with repository ID is scoped to that remote repository only. For example,
to disable resolution of prefix file on Maven Central use following configuration:
`aether.remoteRepositoryFilter.prefixes.resolvePrefixFiles.central=false`.

## Known issues

As can be seen, most often issue reported by our users is that in some environments, usually with MRMs involved,
have their builds mysteriously fails. As it turned out, certain MRMs "group/virtual repository" feature is leaky, and hence,
the virtual repository root allows discovery of a prefix file, but in fact it is "leaking" from one of it's member repositories.
Hence, Resolver will fail to resolve all GAVs available from that repository, given the valid prefix file it served contains
only a "slice" of available GAVs. In this case, user can disable prefix resolution (and even provide his own). 

In these case, please pressure MRM vendor to fix these resource leaks (I'd be asking myself, what else is leaking in?).
Ideally, all Maven supporting MRMs should support prefix file generation, and doing that is nearly trivial.

Simplest thing when no prefix file support exists is if repository path `.meta/prefixes.txt` emit HTTP 404.

Full support is not more complicated:
* hosted repository prefixes generation is nearly trivial exercise (see `find` example above)
* proxy repository should proxy proxied remote repository (if present, proxy it as is, if absent, report 404)
* group/virtual repository should merge them properly, instead to offer "one random member prefix file"

