# Kaleidoscope product terms — handover for legal review

**Kleos Research Private Limited — 23 August 2026**

Four documents accompany this note:

- `src/data/legal/ENGINE-EULA.txt`
- `src/data/legal/PRIVACY-NOTICE.txt`
- `src/data/legal/SECURITY-POLICY.txt`
- `src/data/legal/SUPPORT-POLICY.txt`

They are published at `https://memory.kleosresearch.xyz/docs/legal/`.
`CC-BY-4.0.txt` is unmodified upstream text and was not touched.

---

## 0. These are unreviewed drafts, and the banner stays

**None of these four documents is in force.** They have not been reviewed by
legal counsel, and the company has not adopted them. They are complete in the
sense that no clause is left to be filled in later — what is outstanding is
review and a decision to adopt, not missing terms.

**The review-draft banner on the website and in each document stays exactly as
it is until sign-off.** It was not removed, weakened, or reworded, and it must
not be. A document that reads as finished is not the same as a document that is
in force, and only a signed-off review makes it the second thing. Nobody
drafting these has the authority to declare them in force.

Two banner artefacts are now slightly out of date in the *conservative*
direction and were deliberately left alone:

- `src/data/legal-index-notice.txt` still says the production entity,
  jurisdiction and contacts are "outstanding". They are now settled in all four
  documents. The sentence understates how finished the drafts are, which is the
  safe direction, so it was not edited. **If you want it corrected, correct only
  that clause and leave the not-in-force statement untouched.**
- `src/pages/.well-known/security.txt.ts` still says no production security
  intake is published — see item 24, which is a genuine problem rather than a
  harmless one.

---

## 1. THE OPEN COMPLIANCE QUESTION — section 12(3)(c), the registered office and the CIN

**This is the first thing for you to decide, and it is not decided here.**

### What each document says

Every one of the four carries this entity block and nothing more:

> Kleos Research Private Limited
> Email: contact@kleosresearch.xyz

together with the statement that it is a private limited company incorporated
in India and registered in Delhi, and an **affirmative undertaking** that full
entity particulars — including the registered office address and the Corporate
Identity Number — are available on request at that address. The undertaking is
worded as a promise to furnish them to anyone who asks, without asking why, and
not merely as a contact line. It appears twice in most documents (entity block
and contact block).

**No registered office address, no CIN, and no placeholder or "to be supplied"
line appears anywhere in any of the four.** That is the owner's decision.

### The provision

Section 12(3)(c) of the Companies Act, 2013 requires a company to have its
name, the address of its registered office and its Corporate Identity Number,
together with telephone number, fax number (if any), email and website
addresses (if any), printed in

> all its business letters, billheads, letter papers and in all its notices and
> other official publications.

### The two readings, set out neutrally

**Reading A — published product terms are an "official publication".** The
phrase is broad and undefined. Terms of service published under the company's
name, which purport to bind users and to identify the contracting party, look
more like an official publication of the company than like marketing copy. On
this reading the four documents should carry the registered office address and
the CIN, and the undertaking to supply them on request does not substitute for
printing them. Rule 26(1) of the Companies (Incorporation) Rules, 2014
separately requires those particulars on a company's **website landing page**,
which is a related and arguably sharper point: it does not depend on how
"official publication" is construed, and it is directed at the website itself
rather than at any document on it.

**Reading B — they are not.** The section is aimed at correspondence and formal
company communications, and its enumerated examples are all stationery
("business letters, billheads, letter papers"). Website terms are neither
correspondence with an identified addressee nor a formal company notice such as
a general-meeting notice or a statutory advertisement. On this reading the
identification requirement is satisfied by naming the company, its type, its
jurisdiction and a monitored contact, with an undertaking to supply the rest.

### Two points that bear on the choice, and no more than that

**Nothing is being concealed.** Both the registered office address and the CIN
are already public on the MCA portal against the company name, and anyone can
retrieve them there in a few minutes. Omitting them from the website therefore
withholds nothing that is not already findable. **The question is one of
compliance form, not confidentiality.**

**The affirmative undertaking is a materially better position than silence.**
A document that says "we will give you these particulars on request" is not the
same as a document that simply omits them. It preserves the practical purpose
of the section — that a person dealing with the company can identify and reach
it — and it is evidence of good faith rather than of an attempt to be
untraceable. Whether that is enough to satisfy section 12(3)(c) if Reading A is
correct is exactly the question we are putting to you.

### What we are asking you to decide

1. Are published product terms an "official publication" within section
   12(3)(c)?
2. If they are, does an affirmative undertaking to supply the particulars on
   request operate as a sufficient substitute, or must they be printed?
3. Independently of 1 and 2, does Rule 26(1) of the Companies (Incorporation)
   Rules, 2014 require the particulars on the site's landing page?
4. Section 12(3)(c) also lists **telephone number**, and that item is *not*
   qualified by "if any" in the way fax number is. No document carries one and
   the undertaking does not name one. Does the company need to publish a
   telephone number, and if so where?

**The drafters take no position on any of these.** The owner has made a
decision, this note records it for your review, and it is straightforward to
add the particulars to all four documents and to the site footer if you
conclude that they are required.

---

## 2. Judgement calls, in the order they matter

Each entry says what was decided, why, and what you may want to change.

### The most consequential

**1. The Agreement now recites its own consideration (EULA cl. 4.1).**
The previous draft said, twice, that no fee is payable for the alpha. An
agreement without consideration is void under **section 25 of the Indian
Contract Act, 1872**, and if the EULA were void as an agreement the warranty
disclaimer in section 13 and the liability cap in section 14 would fall with it
— the exact opposite of the drafting objective. Consideration is available (the
licensee's covenants, the confirmations, the feedback licence, the indemnity,
the confidentiality obligations) but was nowhere recited. Clause 4.1 now names
those promises as the consideration for the licence and says the licence is
granted for them rather than gratuitously, and clause 5.8 cross-refers.
**Confirm this is the shape you want**, and whether you would prefer a nominal
fee instead. This was the single largest structural defect in the previous set.

**2. The warranty disclaimer no longer rests on the Sale of Goods Act (EULA cl.
13.2).** The previous draft relied on section 62 of the Sale of Goods Act, 1930
while clause 7 of the same document said "The Engine is licensed, not sold" and
clause 5.8 said no price passes. Section 4 of that Act requires a sale —
transfer of property in goods for a price — so the document was citing an
enabling provision whose predicate it denied four clauses earlier. The
disclaimer now rests on freedom of contract under the Indian Contract Act,
1872, with section 62 cited **only in the alternative** if and so far as the
Sale of Goods Act applies at all. *Tata Consultancy Services v State of Andhra
Pradesh* (2005) 1 SCC 308 supports software being "goods", but it concerned
packaged software on media in a sales-tax context and does not convert a free
non-transferring licence into a sale.
The same clause now also says expressly that disclaiming a non-infringement
**warranty** does not touch clause 14.1(f), which preserves **liability** for
third-party IP claims. Those two were in tension in the previous draft.

**3. The privacy notice no longer claims a lawful basis that does not exist
(Privacy cl. 3.2, 3.4).** The previous draft said the basis for processing key
validation events was "performance of the arrangement under which we gave you a
key, which is the legitimate use in section 7 of the Act". **Section 7 of the
DPDP Act has no performance-of-contract limb.** Section 4(1) permits processing
only on consent or for "certain legitimate uses", and section 7 is a closed
list: voluntary provision for a specified purpose (a); State functions (b)–(c);
compliance with a judgment or order (d); medical emergency (e); epidemic or
public health (f); disaster or breakdown of public order (g); employment
purposes (h). Nothing covers contract performance. That was GDPR Article
6(1)(b) wearing an Indian name — the precise failure mode the drafting brief
warned against — and clause 3.4 repeated it with "our own obligation to keep
our systems secure" (Article 6(1)(c)/(f)).

Both now rest on **consent alone**, and the notice says why in terms: a purpose
held up by consent *and* something else is a purpose that withdrawal does not
actually stop, which would hollow out the section 6(4) right. The consequence
is stated plainly to the reader — withdrawing consent to the validation
processing ends alpha access. Clause 3.1 retains section 7(a) alongside consent
because voluntary provision for a specified purpose genuinely fits an access
request. Clause 3.4 separates out the CERT-In disclosure as something **required
of us by statute**, which withdrawal does not stop, rather than dressing it as
an section 7 limb.
**If you prefer a single clean basis everywhere, consent alone is defensible in
3.1 too.**

**4. Clause 2 alone does not make this B2B, and a fourth confirmation was added
(EULA cl. 2.2(d)).** The three confirmations in the previous draft — acting for
an identified business, authority to bind it, business purpose — are
**orthogonal to the statutory exception they were written to exclude**. A
self-employed developer can truthfully confirm all three and remain a consumer:
a sole proprietorship *is* a business, acting for it *is* acting for a business,
and using the product in it *is* a business purpose. The Explanation to section
2(7) of the Consumer Protection Act, 2019 preserves consumer status for a person
acquiring services **exclusively for the purpose of earning a livelihood by
means of self-employment**.

Clause 2.2 therefore now carries a fourth confirmation directed at the exception
itself: that you are **not** acquiring the Engine exclusively to earn your own
livelihood by means of self-employment. Clause 2.3 explains it to the reader in
plain terms, conclusion first.

**This still only holds if signup actually collects all four confirmations. It
does not today.** A clause in a document nobody was asked to accept is not a
confirmation. This is a **product change, not a drafting one**:

> Signup must require the person to identify the business they act for, confirm
> their authority to bind it, confirm business purpose, and confirm they are not
> within the self-employment exception — and the company must retain a record of
> each.

**The fork, stated as the fork it is:** if the company decides instead to admit
individual and self-employed developers, these documents must be made
consumer-compatible. That is a different drafting exercise, not an amendment:
the liability cap, the indemnity, the exclusive-jurisdiction clause and the
warranty disclaimer would all have to be re-cut, and clause 2.4 would move from
a fallback to the centre of the document.

**5. The retroactive confirmation was removed (EULA cl. 2.2, closing
paragraph).** The previous draft made the user confirm that all three statements
"were true when you first asked us for access" — about a signup flow that never
collected them. Relying on that in a dispute would mean asserting a confirmation
the user never made, which invites a misrepresentation finding **against the
company**. The clause is now conditional: it back-dates only where signup
actually collected the confirmations, and otherwise says so.

**6. The export promise is gone from all four documents, and this is a real
reduction.** Every previous draft stated in some form that the commands which
inspect, verify, **export** and migrate a store are never gated. **That is
false.** The entitlement gate covers exactly four commands — `serve`, `mcp`,
`context`, `call` — and `call` carries search *and* write. **No ungated command
returns the content of your memories.** Every document now says that instead.

Two consequences you should see clearly:

- **Revocation stops writing as well as reading.** Previous drafts said only
  that it stops serving retrieval. A licensee could reasonably have read that as
  leaving writes alive.
- **The portability position now rests on the storage format, not on a
  command.** Memory text is plain markdown, one file per version; the event
  journal is plain line-delimited JSON; both are readable with ordinary tools
  without the engine and without a key. A database file in the same directory
  holds the derived indexes and the ordering, and that is the part that needs
  the software. This was verified on a current fixture, not assumed.

**If the company wants a portability commitment, it needs a shipped export
command first.** The clause must not be re-broadened ahead of the product. There
is one ungated command with "export" in its name — `vault-export-device` — and
it exports the key material for opening an encrypted vault on a second device,
not memories; each document now says so, because the bare claim "there is no
ungated export command" is falsifiable in one `--help`.

**7. The entire-agreement clause no longer swallows the three non-contracts
(EULA cl. 19.3).** The previous version made "this Agreement and the documents
it refers to" the whole agreement, and the EULA refers to the privacy notice,
the support policy and the security policy — while the support policy and the
security policy each say they are not contracts. A litigator could pick whichever
reading suited: incorporate the support policy to create obligations, disclaim
the safe harbour as non-contractual. Clause 19.3 now says expressly that the
three are referred to for information and are **not incorporated**, with one
exception: the security policy's safe harbour, which the EULA undertakes not to
be used to defeat. The security policy says the same from its side.

**8. The 30-day notice is no longer negated by the clause it sits next to.**
The previous set granted it twice (EULA 12.4 "we will try", Support 12 "we
intend") and removed it once (EULA 5.3: revoke "at any time… and we do not have
to give a reason", unqualified, in the governing document, with the support
policy saying the licence prevails). EULA 5.3 is now expressly subject to 12.4
where we are ending the alpha rather than reacting to something the licensee
did; 12.4 is a firm "at least 30 days"; and the support policy now describes it
as the licence's obligation rather than restating it as its own intention.
**Decide whether you want it firm.** If not, remove it from 12.4 and the support
policy will follow.

### Liability and consumer law

**9. "Gross negligence" was dropped from the carve-outs (EULA cl. 14.1(c)).**
Indian law does not recognise gross negligence as a category distinct from
negligence; it is a US/UK template import. Because it sat in a **carve-out**, an
undefined category widened our exposure unpredictably. The limb now reads
"wilful misconduct", which is what the instruction actually requires.
**This narrows a carve-out — that is, it is in the company's favour — so look at
it if you would rather keep the belt and braces.** Note the related template
tell that was kept: 14.1(a)'s "death or personal injury caused by negligence" is
UCTA 1977 phrasing and India has no UCTA, but the carve-out is protective and
harmless, so it stays.

**10. The indemnity was narrowed and given procedure (EULA cl. 15.2, 15.3).**
The previous draft took an **uncapped** indemnity from a licensee who pays
nothing, while capping the company's own liability at zero. Under **section
2(46) of the Consumer Protection Act, 2019** an "unfair contract" includes a
term imposing an unreasonable obligation or putting a party at a disadvantage,
and **sections 49(2) and 59(2)** empower the State and National Commissions to
**declare such a term void**. If the licensee turns out to be a consumer (item
4), that pair is the first thing declared void, and a court that strikes one
term often reads down its neighbours.

The indemnity is now limited to third-party claims, expressly does not apply to
anything within 14.1, expressly does not apply to a person whose consumer rights
cannot be waived, and carries prompt notice, no-settlement-without-asking, and
a right to take over conduct of the claim. **It is still uncapped in amount** —
say if you want a cap.

**11. The exclusive-jurisdiction clause now carries a consumer-forum carve-out
(EULA cl. 18.3).** The support policy already had one (16.3); the EULA, which
governs, did not. That inconsistency ran in the wrong direction — the weaker
clause was in the controlling document. It now says clause 18.2 does not oust a
forum available to a person as of statutory right.
**This weakens the clause against a claimant who turns out to be a consumer.**
The alternative — a bare exclusive-jurisdiction clause — reads stronger and is
more likely to be read down entirely.

**12. Clause 2.4 was added to the survival list (EULA cl. 12.6).** Clause 14 is
expressly "subject to" 2.4, which preserves non-waivable consumer rights, but
2.4 was not in the survival list. Section 14 would have survived termination
without its qualifier, leaving the cap unqualified. Drafting defect with a real
consequence; fixed.

**13. The controlling Indian doctrine on reading down a cap is *Brojo Nath*,
and it is not cited in the documents.** *Central Inland Water Transport Corp. v
Brojo Nath Ganguly*, (1986) 3 SCC 156 lets a court strike an unconscionable term
in a **standard-form contract concluded on unequal bargaining power** as opposed
to public policy under section 23 of the Contract Act. That is the most likely
route by which an Indian court attacks this cap, and it is the doctrine you
should test the documents against.

The documents cite *Bharathi Knitting Co. v DHL Worldwide Express*, (1996) 4 SCC
704, but **that case is being asked to carry more than it can**: it upheld a
limitation clause in a **commercial contract for consideration**. A cap of
**nil** in a **free** contract is not a limitation, it is a total exclusion, and
courts read total exclusions down far more readily. Items 1 (consideration), 4
(whether the counterparty is a consumer at all) and 10 (indemnity asymmetry) all
feed the same exposure. **The reference list is deliberately kept in the
documents rather than moved here, but *Brojo Nath* is not published in them —
citing the case that would be used against us seemed the wrong side of candid.**

### The privacy notice as a DPDP instrument

**14. The Data Fiduciary line is drawn twice, positively and negatively
(Privacy cl. 1.1; EULA cl. 8.5).** The notice now says not only that Kleos is
not the Data Fiduciary for vault contents, but that it is **not a Data Processor
of them either** — because it never processes them on anyone's behalf and never
receives them at all. The previous draft only said what Kleos was not, which
invites the question "then are you the Processor?". The EULA mirrors it from the
licensee's side: **the licensee is the Data Fiduciary for personal data in their
vault**, in those words.

**15. The exposure ledger is now disclosed in DPDP terms, not just as a
feature (EULA cl. 8.5; Privacy cl. 2.2).** Every ranked search writes a local
record containing the query text, the served context and the memories selected;
a request to suppress it is **refused**, not silently ignored. That means the
product forces the licensee — who is the Data Fiduciary for anything personal in
their vault — to create and retain a processing record they cannot switch off,
which cuts against their own section 8(7) erasure duty and will surface in their
own assessment. The EULA now says so in terms rather than leaving it as generic
"you are responsible" language.

**16. "Each search" was wrong and is now "each ranked search".** A read
addressed to a single memory by its identifier writes **no** exposure record.
The precise wording matters most in the security policy, which invites
researchers to falsify the claims in it.

**17. Retention is re-anchored to section 8(7) (Privacy cl. 7).** The previous
draft justified periods by business need ("so that we can deal with questions
and claims"), which is an Article 17(3)(e) concept. Section 8(7) requires
erasure on withdrawal or when the purpose is no longer served, unless a law
requires retention. The section now leads with that rule and presents the
periods as outer limits within it. The 12-month log figure is unchanged and is
still set by two floors that are not ours to choose: **CERT-In's rolling 180
days within Indian jurisdiction, now**, and **Rule 6(e)'s one-year log
retention from 13 May 2027** — which, unlike Rule 8's erasure regime, applies to
all Data Fiduciaries and not to a notified class. One period satisfying both
beats a shorter one we would have to lengthen. **If you read Rule 6(e) as not
reaching these logs, six months would be defensible.**

**18. Three rights were understated and are now stated correctly.**
- **Section 11** requires the identities of those we shared data with **"along
  with a description of the personal data so shared"**. Clauses 5 and 8 now
  commit to both.
- **Section 5(1)(iii)** requires the **manner** of making a complaint to the
  Data Protection Board, not merely a pointer to it. Clause 8 now describes it —
  online, to the address the Board publishes, with what to include — and
  undertakes to supply our correspondence in an attachable form.
- **Section 13(3)** makes exhausting our grievance process a **condition** of
  approaching the Board. The previous draft said only "you should normally raise
  the matter with us first". Stating it correctly **favours the company**, and it
  is now stated correctly in clauses 8 and 9.

**19. The children clause dropped "knowingly" (Privacy cl. 12).** "We do not
knowingly process the personal data of a child" is a COPPA formulation. **DPDP
section 9(1) has no knowledge qualifier** and requires verifiable parental
consent before a child's data may be processed at all. The clause now says we do
not process a child's personal data, and that we have built nothing to obtain
verifiable parental consent, so it is not something we are equipped to hold
lawfully. Note that under Indian law a child is anyone **under 18** — not 16, not
13.

**20. Safeguards are now mapped to Rule 6 (Privacy cl. 14), including the
items we do not yet have.** The previous section described what we do and
omitted at-rest encryption on our own side, backups, and processor contracts —
all of which Rule 6 prescribes. The section now walks Rule 6(a)–(g) in order and
**marks which are in place and which are undertakings for a service that is not
finished**. That is a visible admission; it is also the truth, and Rule 6 will
be checked against this list.

**21. Server-side statements are now marked as commitments rather than
descriptions (Privacy cl. 3.2, 14).** "We store a one-way digest of the key",
"the service rejects a request carrying any other field", the retention periods,
transport encryption and access control are all properties of a validation
service whose source is in a separate repository. They could not be verified.
The notice now says which statements you cannot check from your own machine and
that we would rather say so than present them as if you could — matching the
hedge the security policy already used for the same fact. **These must actually
be implemented before adoption, not after.**

**22. The alpha key is stated as personal data, and the cached record is
described completely (Privacy cl. 3.2).** The cached verdict also carries the
identifier we assigned to the key and the key's expiry, both of which are
personal data on the notice's own reasoning. Previously only the digest was
mentioned.

**23. The itemisation is given a Rule 3 form (Privacy cl. 3).** Rule 3 requires
the notice be presented **independently of any other information** and requires
a communication link. Clause 3 now names the standalone URL and undertakes that
any consent request will carry the itemisation and the link with it rather than
pointing at a notice the person must go and find. **Whether one section of a
sixteen-section document satisfies "independently" is a judgement you should
make**; the alternative is publishing clause 3 as its own page.

### Product facts that were wrong and are now right

Each of these was verified against the source. **None of them was a drafting
choice — they were false statements about the product.**

**24. The probe does not run with a cleared environment (EULA 9.2, Privacy 2.4,
Security 9).** All three documents said it inherits nothing. In fact the engine
calls `env_clear()` and then sets three variables back: the control-plane
origin (**set, not forwarded**, so an inherited variable cannot redirect the
call), the entitlement directory the engine resolved, and **the alpha key, read
out of the parent process's environment**. The old sentence "it cannot inherit
an alpha key… or a path" was falsifiable by one `ps`, in the section that
explicitly dares researchers to falsify it. All three now describe the three
variables and say why each is there. **The true version is very nearly as
strong as the false one.**

**25. The "only platform ever built and run" claim was softened.** Four
documents and two product pages said macOS on Apple Silicon is the only
platform on which anything has been built or run. The repository's own CI
configuration defines a **six-cell matrix** that builds and tests on Linux
(x64/arm), macOS (arm/Intel) and Windows (x64/arm), four of them with a runtime
baseline. The absolute claim survives only if that workflow has **never
executed**. The documents now say macOS on Apple Silicon is the only platform we
**support** and the only one **we have run it on ourselves**, and that the build
configuration also compiles and tests elsewhere but that no other build is
supplied or supported. **That wording is true either way.**
> **Confirm from the Actions run history whether the matrix has ever run.** If
> it has, the two product pages (`status.mdx`, `compatibility.mdx`) still carry
> the absolute claim and need the same treatment. They were left alone as
> outside the scope of this drafting pass.

**26. The client has no request validator, and the wording now reflects that
(Security 9, Privacy 3.2).** The previous text said "any other field in that
body is rejected before the request is built", implying a validator. The request
struct is serialise-only with two fields; its own comment claims
`deny_unknown_fields`, but that is inert on a type nothing decodes into. The
true and equally reassuring statement is that **there is no code path that can
add a third field**, and that is what the documents now say. The *server's*
rejection behaviour remains a commitment (item 21).

**27. The 24-hour and 7-day figures are ceilings, not settings (EULA 9.6,
Privacy 3.2, Security 9).** The verdict carries a server-supplied revalidation
interval and grace period, clamped **on read** at 24 hours and 7 days so an
edited cache file cannot buy a longer window. **The server can make checks more
frequent** — which would have made "at most once a day" false while the 8-day
worst case stayed true. The documents now describe the mechanism, and the 8-day
outer limit on revocation is unchanged and correct.

**28. The failure-state contact rate is now disclosed (Privacy 3.2).** While a
verdict is stale, denied, revoked or absent, the probe may re-spawn **every 15
minutes** — and on the first check after a key is issued or changed there is no
throttle at all. "At most once a day per installation" was true only of normal
operation. Frequency of contact is a processing fact, so it is disclosed.

**29. Encryption at rest does not protect a mounted vault (EULA 8.3, Privacy
2.5, Security 10).** The product's own capability string says
`plaintext is accessible while mounted`. None of the previous drafts said so,
and a researcher who finds a mounted vault readable would reasonably believe
they had found something. Now stated, with the plain-English version: it
protects the vault when it is closed, not while you are using it.

**30. Two stores outside the vault are now named (EULA 8.2, Privacy 2.6).** The
local **profile store** — vault paths, workspace, principal and journal
identifiers — and the entitlement verdict cache both live in the per-user
application configuration directory at owner-only permissions. The EULA's
enumeration of "what is written there, so you can protect it properly" covered
only the vault. Opt-in diagnostic tracing that writes memory-derived text
outside the vault is also flagged, with the "in normal operation" qualifier the
enumeration needed.

**31. The build check does not cover the one component that opens a socket
(Security 9).** The offline check's own source records that the entitlement
probe "lives outside `crates/`, outside the root workspace and outside
`kaleidoscope-service`'s resolved closure, so it is invisible to this checker's
source glob". The security policy already published the check's other limits
honestly (source text only, no syscall tracing, runtime component Linux-only);
this one was missing. It is now stated, with an offer to supply the probe's
source on request. **This weakens the strongest security claim in the product,
in print, deliberately** — the section invites falsification, and a claim that
does not survive a two-minute check would poison the rest of it.

**32. The website's browser-storage disclosure was corrected, on the site as
well as in the notice.** The live privacy page said the site uses **no local
storage**. It uses two: the theme choice in `localStorage` (persistent) and the
sidebar state — open groups, scroll position and a check value — in
`sessionStorage` (per tab). The notice states the correction in terms, and
**`src/content/docs/docs/privacy.mdx` was fixed** so the site no longer
contradicts its own notice. No cookies are set anywhere; that part was right.

**33. The package-registry claim is narrowed to the Engine (Security 2, 10).**
The npm channel is genuinely publish-blocked (dry-run by default, real publish
behind a token gate). But a **placeholder package has been built for PyPI** to
reserve a name, and whether it was ever uploaded could not be determined
locally. The Engine-scoped claim survives either way, because a reserved name
holds no product, and the security policy now says exactly that.
> **Confirm whether `kscope-memory` was uploaded to PyPI.** If it was, the
> unqualified "not published to any package registry" would have been false.

### The security policy's safe harbour

**34. The safe harbour was recast from a promise into a standing authorisation
(Security cl. 6.1).** This is the most substantive change in that document. As a
promise it needed **estoppel** to bite, and promissory estoppel against a
**private** party in India is far narrower than against the State — it rests on
section 115 of the Evidence Act (section 121, Bharatiya Sakshya Adhiniyam), not
on the *Motilal Padampat* line. As an **authorisation** it needs nothing:
**sections 43 and 66 of the Information Technology Act, 2000** turn on whether
access was **without the permission of the owner**, so our permission is a
**fact contemporaneous with the research**, needing neither estoppel nor
consideration. The undertakings not to sue, not to complain and to state on the
record that access was authorised are demoted to consequences of the
authorisation rather than being the whole of it.

**35. An inadvertent-overstep limb was added (Security cl. 6.3).** Clause 2.2
forbids testing the validation endpoint, and clause 6 covers only research
inside 2.1 — so a researcher who probed the endpoint and found something real
would have been outside the harbour. Now: stop, do not go back, tell us, delete
what you took, and it is treated as inside 6.1.

**36. "Civil or criminal" was conformed rather than corrected two paragraphs
later (Security cl. 6.1).** A private party in India cannot bring criminal
proceedings; it files a complaint or an FIR and the State decides. The first
bullet now says that, and 6.4 explains the limit rather than quietly fixing the
overstatement above it.

**37. The document is a draft with one live clause, and that tension is real.**
The status block and clause 13 both say clause 6 is meant to be relied on now,
including for research already done — while the site banner says "Do not rely on
this text". **The substance is right** (a safe harbour nobody can rely on is
worthless) **and the packaging is unresolved.** Recasting it as an authorisation
reduces the dependence on estoppel but does not remove the oddity.
> **Decide between:** (a) extract clause 6 and adopt it separately as a
> one-page disclosure statement that **is** in force, leaving the rest a draft;
> or (b) leave it as it stands. Do not resolve it by deleting the reliance
> sentence and keeping the harbour — that is the worst of the three.

**38. Response-time targets stay deleted, and a publication date was added
instead (Security 5, 7).** The brief directs best effort with no committed
timeline. But a best-effort promise with **no** fallback is a way of keeping a
researcher quiet indefinitely, so clause 7 now gives a hard number in the
researcher's favour: **no substantive response within 90 days and you may
publish, inside this policy.** Clause 5 points at it. Previously clause 7 said
only "a reasonable period, if we have gone silent", which is vague exactly where
a non-responsive company would want it to be.

**39. Vulnerability reports are carved out of the feedback licence (EULA 11.3;
Security 3; Support 9).** The EULA takes a broad licence in "feedback", and the
support policy said in terms that a report is feedback — while the security
policy told researchers their report was unencumbered and never mentioned it.
Researchers care intensely about this. Reports under the security policy are now
expressly **not** feedback, in all three documents.

**40. The feedback licence was softened for section 30 of the Copyright Act
(EULA 11.1, 11.4).** **Section 30 of the Copyright Act, 1957** requires a
licence to be **in writing signed by** the owner — here the user — and section
19 does the same for assignments. A click-accept is arguably "writing";
"**signed**" is satisfied only by an electronic signature meeting sections 3 or
3A of the IT Act (a digital signature or a Government-notified authentication
technique), and **a checkbox is not one**. Section 10A of the IT Act validates
contracts formed electronically but does not supply the section 19/30 signature.
Note also **section 19(4)**: a grant not exercised within one year lapses.
Clause 11.1 is now a non-exclusive licence "to the fullest extent you are able
to grant it", with 11.4 as a fallback covenant not to assert rights against our
use of the ideas and information. **This does not affect the licence we grant in
clause 4** — Kleos is the licensor there and can sign.

**41. Confidentiality is now reciprocal (EULA cl. 17.2).** The previous clause
bound the licensee on our non-public information and owed nothing in return, in
a document that elsewhere invites them to send us diagnostics. We now owe the
same duty on what reaches us in support and security correspondence. The
security policy cross-refers.

### The support policy

**42. The stale cross-reference to "response targets" was fixed (Support
3(a)).** It said the security policy "sets out response targets… and that
document says so". The security policy says the **opposite** — it refuses to
give any. That was a flat contradiction between two published documents about
what the company promises. It now says the security policy does not promise a
response time either, and points at the 90-day publication date instead.

**43. The triple disclaimer was cut to one (Support 3).** "It is not an
undertaking… it is not capable of being relied on… it does not become a
commitment by being repeated" read as lawyering around a sentence someone wanted
protected. One disclaimer is more credible than three: "That is a description of
what has tended to happen, not a commitment."

**44. A tester with a key and no repository access now has somewhere to go
(Support 4.1).** The policy says support is repository issues and nowhere else,
that the repository is private, and that email is not a support channel — which
left a hole. Now: ask for access at `contact@kleosresearch.xyz`, described as a
gap in the setup rather than a decision.

**45. "Not intended to create legal relations" was reconciled with the
jurisdiction clause (Support 13.1; Security 13).** A jurisdiction clause and a
continued-use variation clause are contractual terms and cannot sit in an
instrument that disclaims any intention to create legal relations. Both
documents now say they are descriptions, not contracts, **and** that the
governing-law and jurisdiction provisions are there for the case where some part
is nevertheless treated as having legal effect. The support policy's
continued-use variation language was also removed: a changed policy now
"describes how support is handled from the date it is published" rather than
purporting to bind by continued use.

**46. Support 12's 30-day statement now defers to the licence rather than
restating it** (see item 8), and 12.3 explains the storage-format portability
position including the database file that does need the software.

### Readability

**47. The four gated commands are named everywhere.** Previous drafts described
them ("the ones that run the service, expose it to an agent…") and the security
policy gave three descriptions for four commands. They are now named — `serve`,
`mcp`, `context`, `call` — in every document. The whole point of those clauses is
precision about what stops working.

**48. Conclusion-first rewrites.** EULA 2.3 (self-employment) now opens with the
conclusion and then the reasoning; Privacy 13 opens with "until 13 May 2027 the
older IT Act rules apply and this notice already meets them" before the section
44(2) chain; Privacy 3.2's key paragraph now opens with "the key itself is
personal data" instead of ending with it; EULA 14.8's cross-reference is spelled
out instead of sending the reader to 19.5 and back.

**49. A note addressed to the reviewer was removed from a published document.**
The security policy's source list said of the IT Act citations: "the reviewer
should check them against the current consolidated text." That is this note's
job, not the policy's. **It is repeated here as a live request:** please check
sections 43, 66, 70B(6) and 72A against the current consolidated text, since the
Bharatiya Nyaya Sanhita and the Bharatiya Sakshya Adhiniyam have renumbered
neighbouring provisions.

**50. The EULA now says nobody is licensed under it yet.** The status block
protected the company from being held to its promises while clauses 12.1 and 2.2
described, in the present tense, exactly what alpha testers are doing today — so
a developer with a key and a complete published EULA had every reason to think
the licence had attached, indemnity and all. The status block now says that no
one has accepted it, that holding or using a key today is not acceptance and is
not any of the confirmations, and that we will ask when we adopt it. **This
strengthens the banner rather than weakening it.**

**51. The privacy notice now separates what binds anyway from what we are
volunteering.** Some of it — the IT Act rules, the CERT-In directions — applies
whether or not the draft is adopted. The status block says which is which, so
"not in force" is not read as covering obligations that exist regardless.

---

## 3. Findings considered and rejected

**R1. That the on-disk journal is not JSON lines under the default storage
engine.** A reviewer read the engine's "There is no journal frame body" comment
as meaning the JSONL journal does not exist on redb, which is now the default,
and proposed weakening the portability sentence in the support policy and the
EULA. **Rejected on evidence.** The comment describes what the redb *tables*
store, not the on-disk layout. Inspection of a current redb-seeded fixture found
`records/memory/…/versions/…/content.md` as plain markdown, one per version, and
`events/segments/00000000000000000001.jsonl` as plain line-delimited JSON, with
the database file holding only identity, ordering and derived indexes — exactly
what the two-store rule in the engine's own source says. The documents do,
however, now name the database file and say it is the part that needs the
software, which was the useful half of the point.

**R2. Editing the review-draft banner files.** Both `legal-draft-notice.txt` and
`legal-index-notice.txt` were left byte-identical. The index notice's "entity,
jurisdiction, contacts… outstanding" clause is now stale, but it understates how
finished the drafts are, which is the safe direction. Recorded at item 0 for the
owner to decide.

**R3. Editing `.well-known/security.txt`.** It carries a status banner ("no
production security intake is published") and its contact line points at a page
rather than an address. Changing it would mean asserting a live security intake
on a machine-readable file, which is a status declaration rather than a drafting
fix. **Left alone, and disclosed instead**: the security policy's status block
now tells the reader that security.txt has not been updated and that the address
in clause 1 is the one to use. See item 24 in the outstanding list below — this
needs fixing, by someone with authority to change the site's published status.

**R4. Adding a CIN, a registered office, or a placeholder for either.**
Excluded by the owner's settled decision. No blank, no "to be supplied" line, no
invented value. Section 1 above puts the question to you instead.

**R5. Adding any third-party model attribution, or naming the model
"Potion".** Excluded: the embedding model is stated as independently
implemented and trained from random initialisation, carrying no third-party
model artifacts, so there is nothing to attribute. It is called "the Kleos
embedding model" throughout. This was taken as given and **was not verified
against the repository**; see the confirmation at item 1 of the outstanding
list. The word "Potion" appears nowhere in the four documents or the built site.

**R6. Publishing *Brojo Nath* in the documents.** The case is the most likely
route by which a court would read down the liability cap. Citing, in our own
terms, the authority that would be used against us seemed the wrong side of
candid. It is at item 13 above instead, where you will actually use it.

**R7. Keeping "gross negligence" as a separate carve-out.** See item 9.

**R8. Softening the alpha failure list in Support 8**, which includes "defects
that lose or corrupt data". It is candid to the point of being quotable against
the company. It was kept, because it is the sentence that makes the as-is
disclaimer credible; a support policy that omits it is worse. **Flagged so you
can overrule it.**

**R9. Extending the drafting pass into the product pages.** `status.mdx` and
`compatibility.mdx` still carry the absolute "only platform ever built and run"
claim (item 25), and `security.mdx` still says there is no security contact
(item 24). Those are product-status pages, not product terms. They need the same
treatment and are listed as outstanding rather than edited here.

---

## 4. Questions the drafters could not resolve

These need someone with authority, information, or both.

1. **Confirm the shipped alpha binary, and the text its licences command
   prints, match EULA clause 3.2** — that the embedding model is Kleos's own
   work and carries no third-party model attribution. The working tree available
   here is stated not to be current, so this was taken as given and not checked;
   the confirmation is a single command against the actual alpha build, and it
   matters because the licences output would otherwise contradict the EULA in
   the licensee's own terminal.
2. **The embedding model has no product name.** All four documents say "the
   Kleos embedding model", which is a description standing in for a name. One is
   needed before general release.
3. **Will signup collect the four B2B confirmations?** If not, the terms do not
   hold on a B2B footing and the consumer-compatible fork opens (item 4).
4. **Has the CI matrix ever run?** Five statements across four documents and two
   site pages turn on it (item 25).
5. **Was `kscope-memory` uploaded to PyPI?** (item 33.)
6. **Who owns the server-side commitments?** The one-way key digest, the
   field-rejection rule, encryption at rest on our side, access control,
   backups, processor contracts, and every retention period are commitments
   about a service whose source was not available. They must be **implemented
   before adoption**, not after (items 20, 21).
7. **A live product defect makes the privacy notice describe a call most testers
   never make.** The engine resolves the alpha key from the environment **or
   from the documented key file**; the probe reads **only** the environment
   variable and has no key-file fallback, and the engine forwards the key only if
   it was in its own environment. A tester who follows the documentation and
   writes the key to the file therefore gets a probe spawned with no key, which
   exits silently (the spawn is fire-and-forget by design), nothing refreshes the
   cache, and entitlement dies at the end of the 8-day window with no
   explanation. **Fix the probe's key-file fallback; the notice then describes
   what actually happens.**
8. **The account and sign-in denial (Privacy 3.6) needs an owner.** Login lives
   in the public manager, not in the engine, and could not be checked here. If
   the manager ever ships with login live, an entire processing surface — an
   identity provider, a device registry, refresh tokens in the OS credential
   store — becomes undisclosed. The notice commits to being updated **before**
   that happens; someone must own that trigger.
9. **The entitlement gate is a non-default build feature.** EULA clause 9.1 is
   hedged accordingly — "the builds we supply to you under this Agreement carry
   that check" — and **that wording should not be tidied** into "the Engine
   checks your entitlement". A build without the gate makes no network call at
   all, which means the privacy notice over-discloses for it. That is the safe
   direction, but the notice should not be read as asserting the call always
   happens.
10. **Signed and notarised builds exist as a workflow.** The documents say "not
    signed or notarised **for production distribution**", which survives a
    preview build. But there is a working sign-and-notarise pipeline, and if any
    tester has ever been handed a package from it, they hold a Developer-ID
    signed, notarised, stapled artefact. **Confirm how alpha builds actually
    reach testers.**
11. **Export control instruments are gestured at, not named (EULA 16).** The
    binary ships AES-256 and Ed25519. The relevant Indian instrument is the
    **Foreign Trade (Development and Regulation) Act, 1992** and the SCOMET list
    under the Foreign Trade Policy; if distribution touches a US host, **EAR
    ECCN 5D002 and Licence Exception ENC** are engaged. Decide whether the
    clause should name them.
12. **There is no arbitration clause anywhere.** All four choose Delhi courts.
    Recorded as a deliberate choice: no section 9 or section 11 route under the
    Arbitration and Conciliation Act, 1996, no institutional rules, no
    confidentiality of proceedings.
13. **An exclusive Delhi jurisdiction clause is valid only where Delhi courts
    would otherwise have jurisdiction** under sections 16 to 20 of the Code of
    Civil Procedure. The registered office is what ordinarily supplies that —
    the same value the documents omit. The omission therefore has a practical
    edge as well as the formal one in section 1.
14. **Third-party open-source attribution remains incomplete (EULA 10).** The
    engine's own licences command records that Rust dependency notices "are not
    embedded here yet" and that several carry attribution obligations. This is a
    **live compliance gap**, separate from the model question, and the clause
    admits it and undertakes to supply the list on request. It must be closed
    before general release.
15. **The 35-day backup window and the one-month grievance response are
    operational promises**, not legal findings. Both need an owner before
    sign-off.
16. **The section 43A / section 44(2) analysis is the drafters', and section 13
    of the privacy notice rests on it.** We read section 43A as omitted by
    section 44(2), and section 44(2) as sitting in the 13 May 2027 tranche —
    hence section 43A and the SPDI Rules 2011 are live today, which is why the
    notice commits to SPDI Rule 5(9)'s one month rather than Rule 14's ninety
    days. Circulating sources disagree on the tranche mapping (some render the
    stages as 14 November / 14 November / 14 May, one prints the third stage as
    March 2027). **The dates below were taken as given; the section 44(2)
    placement should be checked independently.**
17. **The website's landing page** does not carry the company particulars — see
    Rule 26(1) at section 1, question 3.

---

## 5. Indian-law points relied on, with citations

**Contract**
- **Indian Contract Act, 1872, s.10** — what makes an agreement a contract;
  **s.25** — an agreement without consideration is void (EULA cl. 4.1, item 1);
  **s.23** — an agreement whose object is unlawful or opposed to public policy
  is void (EULA cl. 14.1); **s.28** — an agreement in absolute restraint of
  legal proceedings, or one curtailing the limitation period, is void to that
  extent (EULA cl. 14.7, Support cl. 16.3, Security cl. 13).
  https://www.indiacode.nic.in/bitstream/123456789/2187/2/A187209.pdf
- **Limitation Act, 1963** — the limitation periods the documents leave intact.
- **Central Inland Water Transport Corp. v Brojo Nath Ganguly, (1986) 3 SCC
  156** — an unconscionable term in a standard-form contract concluded on
  unequal bargaining power may be struck as opposed to public policy under s.23.
  **The most likely route by which the cap is attacked** (item 13).
- **Bharathi Knitting Co. v DHL Worldwide Express, (1996) 4 SCC 704** — an
  agreed limitation of liability is given effect unless the clause is itself
  shown to be invalid. Cited in the EULA; **note its limits** (item 13).

**Consumer**
- **Consumer Protection Act, 2019, s.2(7) and its Explanation** — "consumer" is
  defined by the purpose of acquisition, and consumer status is preserved for a
  person acquiring goods or services exclusively to earn a livelihood by means of
  self-employment (EULA cll. 2.2(d), 2.3, 2.4; Support cl. 14.2).
  https://www.indiacode.nic.in/bitstream/123456789/16939/1/a2019-35.pdf
- **s.2(46)** — "unfair contract", including a term imposing an unreasonable
  obligation or putting a party at a disadvantage; **ss.49(2) and 59(2)** — the
  State and National Commissions may declare such a term void (item 10).

**Sale of goods**
- **Sale of Goods Act, 1930, s.62** — implied rights, duties and liabilities may
  be negatived or varied by express agreement. **Relied on in the alternative
  only**, because s.4 requires a sale for a price and this is a free licence
  (item 2). **Tata Consultancy Services v State of Andhra Pradesh, (2005) 1 SCC
  308** — software as "goods", in a sales-tax context.

**Copyright**
- **Copyright Act, 1957, s.19** (assignment in writing signed by the owner),
  **s.19(4)** (a grant not exercised within one year lapses), **s.30** (a licence
  must be in writing signed by the owner) — the reason the feedback licence is
  hedged (item 40). **Information Technology Act, 2000, ss.3 and 3A** (what
  counts as an electronic signature), **s.10A** (contracts formed
  electronically are not unenforceable for that reason alone).

**Data protection**
- **Digital Personal Data Protection Act, 2023** — s.2 definitions (Data
  Fiduciary, Data Processor, Data Principal, Consent Manager); **s.4(1)**
  (consent or certain legitimate uses); **s.5** (notice), **s.5(1)(iii)**
  (manner of complaining to the Board), **s.5(3)** (Eighth Schedule languages);
  **s.6(4)** (withdrawal as easy as giving); **s.7** — the closed list of
  legitimate uses, with **no contract-performance limb** (item 3); **s.8(7)**
  (erasure on withdrawal or when the purpose is spent), **s.8(9)** (published
  contact); **s.9(1)** (verifiable parental consent), **s.9(3)** (no tracking or
  targeted advertising directed at children); **s.10** (Significant Data
  Fiduciary designation by the Central Government); **s.11** (access, including
  a description of the data shared); **s.12** (correction and erasure);
  **s.13(3)** (Board complaint conditional on exhausting the Fiduciary's
  grievance process); **s.14** (nomination); **s.15** (Data Principal duties);
  **s.16** (transfer to any country except one restricted by notification);
  **s.44(2)** (omission of s.43A of the IT Act).
  https://www.indiacode.nic.in/bitstream/123456789/20063/1/a2023-22.pdf
- **Digital Personal Data Protection Rules, 2025** — **Rule 3** (itemised
  notice, presented independently, with a communication link); **Rule 6**
  (security safeguards: protection of stored data, access control, logs,
  continuity, log retention, processor contracts, means of enforcement);
  **Rule 6(c) and 6(e)** (access logs, one-year retention); **Rule 7** (breach
  intimation to the Board, detailed report within 72 hours); **Rule 9**
  (published business contact); **Rule 14** (means of making a request, response
  within a reasonable period not exceeding 90 days); **Rule 15** (transfer).
  https://www.dsci.in/files/content/documents/2025/Digital-Personal-Data-Protection-Rules-2025.pdf
- **Information Technology Act, 2000, s.43A and s.72A**, and the **Information
  Technology (Reasonable Security Practices and Procedures and Sensitive
  Personal Data or Information) Rules, 2011** — the operative regime until
  13 May 2027; **Rule 5(9)** requires grievance redressal within one month,
  which is the period the privacy notice adopts.
- **CERT-In directions of 28 April 2022 under s.70B(6) of the IT Act, 2000** —
  6-hour incident reporting; ICT system logs enabled, maintained securely for a
  rolling 180 days, **within Indian jurisdiction**. **In force now, independent
  of the DPDP commencement timetable**, and capable of being triggered by an
  incident involving no personal data at all.
  https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf

**Computer misuse**
- **Information Technology Act, 2000, ss.43 and 66** — both turn on access
  **without the permission of the owner**, which is why the safe harbour is
  drafted as an authorisation rather than a promise (item 34). **s.70B(6)** —
  the CERT-In direction power. **s.72A** — disclosure in breach of a lawful
  contract; not repealed by the DPDP Act.

**Companies**
- **Companies Act, 2013, s.12(3)(c)** — name, registered office address and CIN,
  with telephone number, fax number (if any), email and website addresses (if
  any), in business letters, billheads, letter papers and **all notices and
  other official publications**. See section 1.
- **Companies (Incorporation) Rules, 2014, Rule 26(1)** — particulars on the
  website landing page. See section 1, question 3.

**Procedure**
- **Code of Civil Procedure, 1908, ss.16 to 20** — an exclusive-jurisdiction
  clause is valid only where the chosen court would otherwise have jurisdiction
  (item 13 of the outstanding list).

---

## 6. DPDP commencement dates that matter

Taken as given for this draft and **not independently re-derived**. The official
commencement notification is:

https://www.meity.gov.in/static/uploads/2025/11/c56ceae6c383460ca69577428d36828b.pdf

| From | What commences |
| --- | --- |
| **In force now** (since 13 November 2025) | The definitions, and the provisions constituting the **Data Protection Board of India** and conferring its powers. |
| **13 November 2026** | The **Consent Manager** provisions — registration of Consent Managers and their obligations. |
| **13 May 2027** | The **principal obligations** — notice, consent, the duties of a Data Fiduciary, Data Principal rights, the **Significant Data Fiduciary** provisions, and the **cross-border transfer** provisions. |

The Rules were notified on 13 November 2025 and published in the Gazette the
following day; both dates circulate and refer to the same instrument.

**Three consequences the privacy notice turns on:**

1. **Until 13 May 2027 the operative regime is section 43A and section 72A of
   the IT Act, 2000 and the SPDI Rules, 2011.** Section 43A is omitted by
   section 44(2) of the DPDP Act, and that sub-section is itself in the 13 May
   2027 tranche — which is why section 43A is still live today. Section 72A is
   not repealed and continues afterwards. **This chain is the drafters' reading;
   please check it** (outstanding item 16).
2. **The notice is written to the DPDP standard now.** The rights in clause 8
   and the grievance process in clause 9 are offered today, whether or not the
   provision requiring them has commenced, and the notice says a Data Principal
   exercising one now will not be told to come back in 2027. **That is a
   voluntary commitment**, and it is one of the things that does not bind until
   the notice is adopted.
3. **Rule 6(e)'s one-year log retention arrives on 13 May 2027** and, unlike
   Rule 8's erasure regime, is not limited to a notified class. Combined with
   CERT-In's 180 days, which binds now, it sets the 12-month log period (item
   17).

**Significant Data Fiduciary status is not self-assessed.** Under section 10 the
**Central Government designates**, having regard to the volume and sensitivity
of data processed, the risk to Data Principals, the potential impact on the
sovereignty and integrity of India, the risk to electoral democracy, the
security of the State and public order. The notice says the company has not been
designated, that no SDF obligation therefore applies, that it claims no
exempting self-assessment, and that designation looks unlikely at this scale —
**as an observation about scale, not a determination the company is entitled to
make**. The provision has not commenced in any event.

---

## 7. A structural request

Six facts appear in more than one document, and **five of the six had already
drifted** between drafts: the gated command set, the revalidation and grace
numbers, the on-disk formats, the notice period, whether the security policy has
response targets, and the request-body rejection rule. Every one of those
drifts produced a contradiction between two published documents.

**Before sign-off, and again at every release, the four documents should be
checked against a single table of those cross-document facts.** The security
policy's clause 9 explicitly invites researchers to falsify exactly these, and
the entitlement gate that supplies most of them is very new code.

---

## 8. Status of the site as it stands

- The four documents in `src/data/legal/` have been rewritten and the site
  rebuilt and promoted, so the published pages carry the new text.
- The build gate and all nineteen site tests pass.
- `CC-BY-4.0.txt` is untouched.
- **Both review-draft banner files are untouched**, and the four documents each
  carry the not-in-force statement in their own text.
- Nothing has been committed, pushed, or proposed as a pull request. Every
  change is local.
- **The banner stays until you sign off.** These documents become terms when
  that happens, not when they read as finished.
