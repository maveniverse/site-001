---
title: "Handling sensitive data in Maven"
date: 2024-12-07T12:56:00+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - encryption
  - settings
projects:
  - Maven

---

Maven is well known for flexible configurability. Many times, those configuration and setting
files can contain sensitive data (like passwords). Long time ago, it was even common practice
to put `gpg.passphrase` in POM properties! The latest GPG plugin releases introduced 
`bestPractice` parameter, that when enabled, prevents getting the GPG passphrase in
"insecure" ways. Furthermore, new versions of GPG plugin will flip the default value
and finally remove all the related parameters (see [MGPG-146](https://issues.apache.org/jira/browse/MGPG-146)
for details).

But GPG is not the only thing requiring "sensitive data". There are things like server passwords,
and many other things, that are usually stored in `settings.xml` servers section, but also
proxy passwords and so on.

Maven3 introduced [Password encryption](https://maven.apache.org/guides/mini/guide-encryption.html)
that was introduced as "the solution", but technically it was very suboptimal.

Maven4 will change radically in this area. For start, Maven4 will rework many areas of "sensitive
data" handling, and it will be **not backward compatible** with Maven3 solution, while Maven4
will support "obfuscated" Maven3 passwords (at the price of nagging user).

## The problems

Maven3 password encryption, without going into details, had several serious issues, In fact, we
call it "password obfuscation" as by design, it seemed more close to it. Problems in short:

Cipher used to encrypt was flawed - as explained in [this PR](https://github.com/codehaus-plexus/plexus-cipher/pull/23) 
that also fixed it. But alas, the fix was not backward compatible, it would require all the
Maven3 uses would be forced to re-encrypt their passwords, and moreover, it would still not
solve the fundamental issue.

["Turtles all the way down"](https://en.wikipedia.org/wiki/Turtles_all_the_way_down): Maven3
password encryption encrypt server passwords using "master password". And where was master
password? On disk. Ok, and how was "master password" protected? Well, it was encrypted in
very same way as server passwords, using "master-master-password". You see where it goes?
Given "master-master-password" is well-known (will leave it as homework for figure it out),
this "encryption" was really just an "obfuscation". Whoever got access to your 
`.m2/settings-security.xml`  was able to access all the rest as well.

Moreover, Maven3 worked in "lazy decrypt" way: it handled (potentially encrypted) sensitive data
as opaque strings, and "just at the point of use" tried to decrypt it (was a no-op if not encrypted)
and make use of it, for example in Resolver Auth. The idea was to "keep passwords safe" from
(rogue) plugins, that have plain access to settings, and would be able to steal it. But alas again,
same those (rogue) plugins had access to `SettingsDecrypter` as well (all is needed is to inject
it), and essentially they **still had access to all sensitive data**. This also caused strange,
and usually too late weird errors as well, like after 5 hours of building Maven could spit
"ERROR: I chewed through all your tests, and now would like to deploy, but cannot decrypt
your stale password; please rinse and repeat". It was never obvious who is to blame here,
stale encrypted password, and simply wrong credentials.

## The Maven4 solution

Maven4 got fully redone encryption, while it does support Maven3 setup at the cost of nagging:
it will warn you that you have "unsafe" passwords in your environment.

Moreover, Maven4 does eager decryption: at boot it will strive to decrypt all encrypted
strings (ah yes, it decrypts all, so even your HTTP headers carrying PT token as well!), 
and will fail to boot if it fails even on one. Your path forward is to clean up your environment 
from stale and/or broken encrypted passwords. Maven4 "security boundary" is JVM process, and
if you think about it, same thing happened in Maven3, as explained above. The difference is
that Maven3 forced on every plugin the burden of decryption, that plus had its own issues
(remember the [MNG-4384](https://issues.apache.org/jira/browse/MNG-4384) and how all the 
plugins were forced to carry their "own" PlexusSecDispatcher component?). Also, you have to be
aware, that encryption **applies to settings only**. So in POM you should not have any sensitive
data, no matter is it encrypted or plaintext.

Second, the Cipher used for encryption is completely reworked and improved. Also,
passwords are now "future-proof" encoded in a way one can upgrade them safely to a new
Cipher.

Finally, turtles are gone. Just like it happened in GPG plugin, Maven4 does not store any
"master password" anymore. What it has instead, is "Master Password Source" that can be
variety of things. Maven4 offers 5 sources out of the box, but those are extensible. 

Sources are:
* Secure Console Prompt
* Secure `pinentry` executable
* Secure `gpg-agent` executable
* Java System Property
* Environment variable

Hence, Maven4 will always try to get the master password from your configured source.
On CI you can make it a "secret" and pass over via environment variable, while on workstation
you can (and should) hook it into `pinentry` or `gpg-agent` that usually provide integrations
with host OS keychains as well.

Maven4 password encryption is handled by the new CLI tool: `mvnenc`.