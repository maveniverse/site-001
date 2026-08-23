---
title: "Meet MWM"
date: 2026-08-22T11:32:00+01:00
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

Maveniverse MWM repository is at https://github.com/maveniverse/mwm and supports currently following goals:
`detect`, `link` and `unlink`. Workspaces can be linked in a tree-like form, if someone is really playful
(but recommendation is rather to keep things simple).

{{% /pageinfo %}}

With Resolver 2.x being used in Maven 3.10.x and Maven 4.x lines (and finally, dropping legacy of Resolver 1.x),
users can start picking up new Resolver 2.x features, something not possible with Maven 3.9 and older versions.

Maveniverse "Maven Workspace Manager" (MWM) is one of these new toys, and is first exclusively 3.10+ only extension
in works.

## Problem statement

Branched development with Maven was always a problem. Usually, given local repository is "mixed bag", on branch
checkout (unless is also branch creation like `git checkout -b feature-01`), users are used to "initialize" their
local repository, so next command was always `mvn install -P quick` or some equivalent of it. This issue is getting
even more painful, when user hops from one to another branch, and those contain binary incompatible changes, 
like in one branch new interface method was added, but on another (unrelated) feature branch, there is no
implementation for it.

Maven 3.9 offered some solutions already, like "split local repository" is for exactly these use cases, but 
using it is not trivial.

What if Maven could help you here more?

## Workspace

The idea is following (and contains several hard assumptions, so this is not "general" solution, more like a 
helper): Maven could be made git-aware (first assumption; you use git for versioning), and, you do want to use
git-worktree feature (second assumption) as your feature branches are long-lived (and/or your repository is huge).

The idea of "workspace" is that Maven determines -- by relevant git information -- where to put what. Usually, users
want "cached artifacts" have available across all their projects, shared. Hence, caches should usually go into
user-wide local repository, the one as we know today as "Maven local repository".

But what about build output? Those artifacts you _install_ with `mvn install`? Well, usually the sentiment is that
users do not want them in shared, globally available in local repository. So where to put them?

## MWM

Maven Workspace Manager is an extension that does exactly this, and relies on Resolver 2.x new features, that is 
much more capable than "only" Resolver 1.x could do with for example split local repository.

MWM performs these steps:
* takes over Repository System Session creation from vanilla Maven
* collects git information of the checkout where Maven was invoked
* detects things (relies on Nisse) like "current branch", "upstream URL" and even worktree checkout.
* using these collected information creates "workspace", that, simplified tells two things: where should Maven cache, and where should Maven install.
* workspace "links" are in fact ["local repository tail"](https://cwiki.apache.org/confluence/spaces/MAVEN/pages/235837219/Chained+Local+Repository+Manager+CLRM) auto-managed (this is why MWM bails out if their use by user is detected)

MWM also introduces a new directory `.mvn-local/`, that should be git-ignored (placed in `.gitignore`) just like
`target/` is git-ignored.

## Examples

For example, a trivial project like [Maveniverse Nisse](https://github.com/maveniverse/nisse), on main (default) branch:

```
[cstamas@angeleyes nisse (main)]$ mvn mwm:0.1.1-SNAPSHOT:detect
...
[INFO] --- mwm:0.1.1-SNAPSHOT:detect (default-cli) @ nisse ---
[INFO] MWM 0.1.1-SNAPSHOT
[INFO] MWM workspace detected
[INFO] ======================
[INFO] WS ID     = origin-github.com-maveniverse-nisse-main
[INFO] WS DIS    = origin-github.com-maveniverse-nisse-main
[INFO] WS cache  = /home/cstamas/.m2/repository-oss
[INFO] WS output = /home/cstamas/Worx/maveniverse/nisse/.mvn-local/build
[INFO] ----------------------
[INFO] Considered properties:
[INFO] git.branchName = main
[INFO] git.remoteName = origin
[INFO] git.remoteUrl = git@github.com:maveniverse/nisse.git
[INFO] workspace.discriminator = origin-github.com-maveniverse-nisse-main
[INFO] workspace.id = origin-github.com-maveniverse-nisse-main
[INFO] ----------------------
...
```

Observe, how WS cache and WS output are set: caches are user-wide (global) and project produced (and installed)
artifacts are local.

Now check out a feature branch (in situ):

```
[cstamas@angeleyes nisse (main)]$ git checkout -b feature-01
Switched to a new branch 'feature-01'
[cstamas@angeleyes nisse (feature-01)]$ mvn mwm:0.1.1-SNAPSHOT:detect
...
[INFO] --- mwm:0.1.1-SNAPSHOT:detect (default-cli) @ nisse ---
[INFO] MWM 0.1.1-SNAPSHOT
[INFO] MWM workspace detected
[INFO] ======================
[INFO] WS ID     = origin-github.com-maveniverse-nisse-feature-01
[INFO] WS DIS    = origin-github.com-maveniverse-nisse-feature-01
[INFO] WS cache  = /home/cstamas/.m2/repository-oss
[INFO] WS output = /home/cstamas/Worx/maveniverse/nisse/.mvn-local/build
[INFO] ----------------------
[INFO] Considered properties:
[INFO] git.branchName = feature-01
[INFO] git.remoteName = origin
[INFO] git.remoteUrl = git@github.com:maveniverse/nisse.git
[INFO] workspace.discriminator = origin-github.com-maveniverse-nisse-feature-01
[INFO] workspace.id = origin-github.com-maveniverse-nisse-feature-01
[INFO] ----------------------
...
```

As one can see, not much changed: in this case, Maven will behave just like before, your branch will "see"
same artifacts that were previously installed.

Where MWM shines is git worktrees. Let's repeat these same steps, but use git-worktree feature, as our
feature will be longer living branch:

```
[cstamas@angeleyes nisse (main)]$ git worktree add ../feature-01
Preparing worktree (new branch 'feature-01')
HEAD is now at cb6d6f8 [maven-release-plugin] prepare for next development iteration
[cstamas@angeleyes maveniverse]$ cd ../feature-01
[cstamas@angeleyes feature-01 (feature-01)]$ mvn mwm:0.1.1-SNAPSHOT:detect
...
[INFO] --- mwm:0.1.1-SNAPSHOT:detect (default-cli) @ nisse ---
[INFO] MWM 0.1.1-SNAPSHOT
[INFO] MWM workspace detected
[INFO] ======================
[INFO] WS ID     = origin-github.com-maveniverse-nisse-feature-01
[INFO] WS DIS    = origin-github.com-maveniverse-nisse-feature-01
[INFO] WS cache  = /home/cstamas/.m2/repository-oss
[INFO] WS output = /home/cstamas/Worx/maveniverse/feature-01/.mvn-local/build
[INFO] ----------------------
[INFO] Considered properties:
[INFO] git.branchName = feature-01
[INFO] git.commonDir = /home/cstamas/Worx/maveniverse/nisse/.git
[INFO] git.remoteName = origin
[INFO] git.remoteUrl = git@github.com:maveniverse/nisse.git
[INFO] workspace.discriminator = origin-github.com-maveniverse-nisse-feature-01
[INFO] workspace.id = origin-github.com-maveniverse-nisse-feature-01
[INFO] ----------------------
[INFO] Linked workspaces:
[INFO]   WS ID     = origin-github.com-maveniverse-nisse-main
[INFO]   WS DIS    = origin-github.com-maveniverse-nisse-main
[INFO]   WS cache  = /home/cstamas/.m2/repository-oss
[INFO]   WS output = /home/cstamas/Worx/maveniverse/nisse/.mvn-local/build
[INFO]   ----------------------
[INFO]   Considered properties:
[INFO]   git.branchName = main
[INFO]   git.remoteName = origin
[INFO]   git.remoteUrl = git@github.com:maveniverse/nisse.git
[INFO]   workspace.discriminator = origin-github.com-maveniverse-nisse-main
[INFO]   workspace.id = origin-github.com-maveniverse-nisse-main
[INFO]   ----------------------
...
```

What happens here? MWM detects this is a git worktree, and auto-links current WS to the one having default branch.
This implies, that in this case you do not need to `mvn install` to populate your locally installed repository,
as they are "tailed" to your (maybe empty) local build output repository.

Stay tuned for more!