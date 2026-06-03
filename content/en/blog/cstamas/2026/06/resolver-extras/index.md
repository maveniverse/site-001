---
title: "Resolver Ideas"
date: 2026-06-03T11:32:00+01:00
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

This post is just "tinkering starter", and will get updated as I progress with PoC, or discuss these ideas with others. 
I just wanted to share the ideas I had, and maybe get some feedback on them, or even better, get some help or hints
where these features would be needed or would be useful.

{{% /pageinfo %}}

Some time I was tinkering about some new features for Resolver, and I was thinking about how to implement them.
So, let me lay down the ideas I had.

All these ideas are envisioned as SPI extension points, and by default (or without SPI implementations) would not 
alter anything of Resolver behavior. Moreover, in this post I am intentionally talking **about Resolver only**,
and did not draw any parallel with Maven, as again, details would be implemented in specific SPI implementation.

Moreover, some of these features may not be feasible for Maven use cases at all, but as I said, this is about Resolver
features only, and Maven is not the only Resolver integration out there, so users of library like MIMA can still
benefit from these extra features, if they want to.

Note: these are just ideas and are locally implemented as "proof of concept" (PoC). Also, in many examples will use
Maveniverse Toolbox, but only as tool, as same output would be produced by `maven-dependency-plugin:tree` as well.

## Conditional dependencies

Condition dependencies are plain `optional` dependencies, that **have activation condition associated**, and based on
condition evaluation, may be activated or not. 

Example: consider following example (very same as in [Quarkus guide](https://quarkus.io/guides/conditional-extension-dependencies)): We have example artifact 
[conditional-a](https://github.com/cstamas/resolver-extras/blob/initial/artifacts/conditional-a/pom.xml), and it declares
optional dependency on [conditional-b](https://github.com/cstamas/resolver-extras/blob/initial/artifacts/conditional-b/pom.xml) 
example artifact.

In this case, the proof of concept (PoC) SPI is looking into POM properties, and `conditional-b` declares it:
`<activationCondition>artifactPresent(org.slf4j:slf4j-api)</activationCondition>`. The PoC implements the rule
`artifactPresent(GAV)` as "if artifact with given GAV is present in the resolved graph, then activate this dependency".

Finally, we have an example project [conditional](https://github.com/cstamas/resolver-extras/blob/initial/examples/conditional/pom.xml)
that declares dependency on `conditional-a`. It also contains a profile `satisfy`, that when enabled, will add
dependency on `org.slf4j:slf4j-api`.

Example run without profile:
```
$ mvn -f examples/conditional/ toolbox:tree
...
[INFO] --- toolbox:0.15.14:tree (default-cli) @ conditional ---
[INFO] org.cstamas.resolver.examples:conditional:jar:1.0.0-SNAPSHOT (origin: central)
[INFO] ╰─org.cstamas.resolver.artifacts:conditional-a:jar:1.0.0-SNAPSHOT [compile] (origin: central)
```

We see "as expected" tree. The optional dependency `conditional-b` is not present. Now, if we run with profile:

```
$ mvn -f examples/conditional/ -Psatisfy toolbox:tree
...
[INFO] --- toolbox:0.15.14:tree (default-cli) @ conditional
INFO] org.cstamas.resolver.examples:conditional:jar:1.0.0-SNAPSHOT (origin: central)
[INFO] ├─org.cstamas.resolver.artifacts:conditional-a:jar:1.0.0-SNAPSHOT [compile] (origin: central)
[INFO] │ ╰─org.cstamas.resolver.artifacts:conditional-b:jar:1.0.0-SNAPSHOT [compile, optional] (origin: central)
[INFO] │   ╰─org.slf4j:slf4j-simple:jar:2.0.18 [compile, optional] (origin: central)
[INFO] ╰─org.slf4j:slf4j-api:jar:2.0.18 [compile] (origin: central)
```

The presence of `org.slf4j:slf4j-api` activated the conditional dependency `conditional-b`, and it was present in 
the tree, along with its own dependencies.

## Capabilities

Capabilities goal is to allow **fulfillment checks on collected graph** and provide early warning or errors, or even some
"intervention" from SPI, like dynamic dependency injection.

The **meaning** of capabilities are left to SPI implementations (ideas: OSGi metadata, JPMS module-info `module-name` 
vs `requires`, or `uses` vs `provides`, ultimately it really depends on the domain SPI targets). The basic idea
is that capabilities can, based on given domain, provide warnings, errors or even automatic dependency injection.

Example: consider following example: We have example artifact [consumer-a](https://github.com/cstamas/resolver-extras/blob/initial/artifacts/consumer-a/pom.xml)
and [provider-a](https://github.com/cstamas/resolver-extras/blob/initial/artifacts/provider-a/pom.xml).

In this case, the PoC SPI is looking into POM properties, and `consumer-a` declares capability as `<capabilityConsumer>slf4j-backend</capabilityConsumer>`
while `provider-a` declares `<capabilityProvider>slf4j-backend</capabilityProvider>`, and capabilities are simple
string labels. Checking is simple label matching on consumer and provider side.

Finally, we have an example project [capability](https://github.com/cstamas/resolver-extras/blob/initial/examples/capability/pom.xml) 
that declares dependency on `consumer-a`. For example's sake, we can invoke this project in three ways:

```
$ mvn -f examples/capability/ package
...
BUILD FAILURE

$ mvn -f examples/capability/ -Psatisfy package
...
BUILD SUCCESS

$ mvn -f examples/capability/ -Pdiscover package
...
BUILD SUCCESS
```

In first case, Resolver while collecting the graph will fail ("unsatisfied capability: no provider for capability `slf4j-backend`") 
as there is no provider for declared consumer capability.

In second case, build succeeds, as producer and consumer are "matched". Note: PoC performs only matching, but does not care
about arity, but a SPI could enforce that capabilities match as `1:1` and fail in case of `1:N` (multiple providers
for same capability are present), but again, this is domain specific.

In third case, profile provides a "hint" for PoC SPI how to "discover" a provider for a capability, and possibly 
inject it as dependency, when required.

## Platform matching

Platform matching would be a way for resolver to "align" certain artifact versions against given, known or 
discovered "platform".

TBD.

## Artifact mapping

Artifact mapping would be a way to map artifacts to alternative artifacts, for example using some lookup mechanism.
It could happen within same repository (like relocation), or across repositories 
(a `RemoteRepository` that would be "redirector").

TBD.

Example use case for mapping within same repository: Define a groupId (assume non-existing on Central) and a mapping for it. For example, define G as
`github.sormuras.modules` and use provided [mapping file](https://github.com/sormuras/modules/blob/main/com.github.sormuras.modules/com/github/sormuras/modules/modules.properties).

Then users of SPI could declare dependencies as:

```xml
<dependency>
  <groupId>github.sormuras.modules</groupId>
  <artifactId>codes.rafael.asmjdkbridge</artifactId>
  <version>1.0</version>
</dependency>
```

and it would make resolver go for artifact

```xml
<dependency>
  <groupId>codes.rafael.asmjdkbridge</groupId>
  <artifactId>asm-jdk-bridge</artifactId>
  <version>1.0</version>
</dependency>
```

Whether artifact identity changes (to mapped) or remains virtual may be matter of configuration.

## Implementation details

All these features are envisioned as SPI extension points, and by default (or without SPI implementations) would not 
alter anything of Resolver behavior. Still, given all these feature are able to dynamically alter the graph, the 
backing idea is shown by this pseudocode (showing what new code is wrapping existing `graph = collect()` call:

```
  boolean success = false
  while(!succes) { // + attempt limit
    if (resolverExtrasSPI != null) {
      resolverExtrasSPI.prepare(resolutionContext)
    }
    graph = collect()
    if (resolverExtrasSPI != null) {
      success = resolverExtrasSPI.check(graph, resolutionContext) << can return true, or ask for repeated collection (w/ modified context) or throw error
    } else {
      success = true
    }
  }
```

But, the thing is, and is not visible from pseudo-code, is that collector **retains all the hot caches**, so basically
subsequent collection is not "full collection", but only "re-collection" of modified graph. But, all steps like collection
and subsequent conflict resolution (both performed by `collect()`) is a must, as for example dependency injection could change the winner(s) in the graph.
Moreover, conditional dependency could trigger a provider injection, and so on.