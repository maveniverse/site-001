---
title: "Principles used to build Maven"
date: 2026-03-21T10:07:53+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - maven
projects:
  - Maven
---

{{% pageinfo %}}

Here "how Maven is done" is being discussed, with a bit of historical overview, to understand the ideas used to 
build Maven, as we know it today (so not **what** it does but **how** it does).

{{% /pageinfo %}}

The first Maven "as we know it" was Maven 2. Maven opted for Plexus as DI container, that was a completely separated
project. On the other hand, Plexus did not come out of blue, it pulls roots from projects like ASF Avalon and ASF
Excalibur, [both defunct today](https://excalibur.apache.org/fortress/features.html). If you look around in this
project, you will find familiar classes and expressions like `AbstractLogEnabled` and "component role" and so forth.

## Managed Components

Maven 2 onward (so Maven 3 and Maven 4 inclusive) follows a programming model laid down along these ideas, that were
incepted and implemented by Plexus. In fact, [Sisu in 5 minute](https://eclipse.dev/sisu/org.eclipse.sisu.inject/index.html), 
as "demo" done by Stuart for Sisu tells the whole story: count how many `new` keywords are in there (and where).

Maven always relied on dynamism and independence of components. The usual pattern is to have an interface, and that
interface is implemented by one or more implementations, that, if are managed, we call components. The client code
always codes against interface, and does not care how the implementations got there in the first place.

This implies that usual things like constructors, are basically and should remain a black box for client code. And this
is one of the expectations in Maven (note: Plexus was NOT able to perform constructor injection, it was able only
for field injection).

Still, Maven does not enforce this style onto "client code". Assuming some third party code "starts" in a Mojo
(which itself is a managed component, with slightly different metadata!) implies that client code "entry point" is
always a managed component, and our users are well aware of this: they inject whatever they have need for, like
`MavenSession` and things like that.

But, once they have all they need from (host) Maven that runs the plugin, Maven does not enforce them to continue along 
this trail: a Mojo author may decide to use "plain Java" usage, and create Mojo own object graph with `new` keyword,
and this is totally fine.

By using this style, Maven managed to provide its well known stability, extensibility and dynamism.

## Plexus Limitations

While the idea was sound, this all happened (and was implemented) in early 2000s. This implies it was in time of Java 1.4
or 1.3? No annotations existed then, and constructor injection (combined with `final` fields => immutable components)
was not possible, at least, by Plexus. Hence, despite the component "looked" immutable via its interface, the backing class
had to be implemented with compromises: Plexus required default constructor, and required one to annotate each field
(or method) with requirement.

This is how a Maven 2 component looked like:
* the [interface LifecycleExecutor](https://github.com/apache/maven/blob/maven-2.2.1/maven-core/src/main/java/org/apache/maven/lifecycle/LifecycleExecutor.java)
* the [implementation DefaultLifecycleExecutor](https://github.com/apache/maven/blob/maven-2.2.1/maven-core/src/main/java/org/apache/maven/lifecycle/DefaultLifecycleExecutor.java)
* the component [Plexus metadata](https://github.com/apache/maven/blob/maven-2.2.1/maven-core/src/main/resources/META-INF/plexus/components.xml#L224-L336) that defined component

Observe what `interface` defined: component role (back then, Plexus treated roles as "string labels", not as types!)
and methods.

The implementation tried at best to do encapsulation and immutability, to some degree: the default constructor was a must. 
Moreover, given Plexus did field or method injections, the `private` fields had no setters, as Plexus
did inject them using reflection. And finally, the "meat" is literally only the methods implementing interface, and other
private helper methods.

This implied even, that this component is not even constructable with "plain Java", like `new DefaultLifecycleExecutor()`
properly, as fields would end up all `null`, and without any means except reflection, to make them non `null`.

Later, or around the same time, it became obvious, how this limitation above poses a huge negative impact: writing 
unit tests is almost impossible (without having fully fledged Plexus container). So setters started to creep in, that
were usually defined on implementation and not on interfaces implementations implement.

## Modern Java and Sisu

With new Java capabilities, things greatly improved: we today can use annotations, no more XML authoring (or generating)
and so on. But one of the biggest thing that changed with Sisu, was ability to create **real immutable components
without any compromise, that are easily testable as well**: by use of constructor injection.

It was modern Java and Sisu, that really "clicked in" for Maven 2 model envisioned in early 2000s!

Since then, many components were migrated from Plexus to Sisu/JSR330, and more importantly, all these change happened 
without any client code required change! 

Unless...

## Where problems may come from

Consider this issue: https://github.com/apache/maven/issues/8982 The original issue, or breakage was `NoSuchMethodError`
happening in a plugin. Obvious Maven problem, is it? Maven broke compatibility, right?

Well, I'd argue: not quite, this is client code issue.

Problem comes from the fact that client code decided to use "plain java" object graph construction using `new`, but **applied these to Maven
managed components**. Remember, there is nothing wrong with `new`, as long you are not in Maven, or, if you are in Maven, 
you do not apply `new` onto _Maven managed components_.

As at this moment, the client code becomes tightly coupled with component implementation constructors, something Maven itself
does not expect! In fact, this move emits expectation, that Maven components must obey to the same rules as in case
of "plain Java". But, Maven _expects_ that managed components are injected, and considers constructors as not part of 
any public API (it is job of DI to deal with). And here everything grinds to halt: Maven cannot progress, cannot improve, 
due this (wrong) client code expectation.

## Things you should never do

If your code is expected to run in Maven, and you use Maven (and related, like Resolver) classes, you MUST obey this
expectation, otherwise you are doomed to fail. This is the sole reason why MIMA provides different runtimes as
well ("embedded", "static" and "sisu") and expects you to get everything you need from `Context`: as it hides this
from you, whether the component was DI constructed ("sisu runtime"), manually ("static runtime") or in fact, was given
by Maven itself ("embedded runtime"), the client side of `Context` is always the same, and hence, your code does not 
need any change.

Extending a managed component is bad practice, just like extending a Mojo. Tampering with implementation
constructors and methods, same!

In any case, if you think you cannot get something you need by injecting a managed component, better create an issue,
instead "shortcut" it with circumventions. It may work for a while, but is doomed to fail at some point. 