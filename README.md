# Reference Field Operational Memory

A low-infrastructure GitHub template for giving ChatGPT durable, user-owned working state across conversations: current state, decisions, durable knowledge, working preferences, routed projects, and cross-repository continuity.

The goal is not to make ChatGPT remember everything. It is to keep the smaller set of information that genuinely needs to survive a conversation somewhere you can inspect, correct, version, and own.

> **A portable continuity layer for serious ongoing ChatGPT work.**

Reference Field Operational Memory is an independent open-source project created by **Reference Field, Inc.** It is not an OpenAI or GitHub product and is not sponsored by or endorsed by either company. See [`DISCLAIMER.md`](DISCLAIMER.md) for practical boundaries and third-party independence.

**Supported release baseline:** **ChatGPT Plus (currently $20/month) or a higher ChatGPT plan**, plus the installed/selected and authenticated **`@GitHub` plugin** authorized for the intended repository and exposing repository read/write actions. **Free and ChatGPT Go are unsupported by this release.** A qualifying plan alone does not establish readiness; setup verifies the actual GitHub capability before reporting READY.

Not sure whether this is worth installing? Read **[`WHAT_TO_EXPECT.md`](WHAT_TO_EXPECT.md)** first. It is the short human-facing description of what should feel different in practice.

## Get started: Create → Connect → Activate

You only need to do this once. You do **not** need Git expertise, a terminal, or knowledge of the repository's internal protocol.

### 1. Create

[**Create my private memory repository**](https://github.com/new?owner=%40me&template_owner=referencefield&template_name=operational-memory&visibility=private)

GitHub should open a new-repository form using this template with **Private** preselected. Choose any repository name, visibly confirm **Private**, and create it.

### 2. Connect

In ChatGPT, install/select the **`@GitHub` plugin** in the message composer, authenticate it to GitHub, and authorize the private memory repository you just created. Prefer access to only that repository when available; unrelated repositories are not needed.

**Requires:** the selected `@GitHub` plugin must be authenticated and expose repository read/write actions for the exact repository. Merely seeing GitHub or the Plugin Directory is not enough. OpenAI also documents a separate GitHub app/connection used for repository search and analysis that may be read-only; that separate limitation is not proof that the selected `@GitHub` plugin cannot write.

### 3. Activate

Copy the URL of your new private repository and send:

> `@GitHub Set up operational memory from <YOUR PRIVATE REPOSITORY URL>.`

That's it.

ChatGPT should verify the supported plan, active/authenticated GitHub plugin, exact repository, Private visibility, safe read/write, verified readback, cleanup of its temporary setup test, and protocol structure without making you perform those technical checks.

Success begins:

**Operational memory: READY**

Then ChatGPT should say **One final step** and give you one completed Custom Instructions block with your repository ID already embedded. It should tell you exactly where to put it:

- **Web/Desktop:** Settings → Personalization → Custom Instructions.
- **Mobile:** Settings → Customize ChatGPT → Custom Instructions.
- Make sure customization is enabled, paste the block **at the top above any existing Custom Instructions**, keep your existing instructions, and save.

The completed bootloader is intentionally tiny, about **487 characters with a current 10-digit repository ID**. You do not need to understand or type the ID yourself.

For dependable repository-backed retrieval or saving, start the message with **`@GitHub`**. The bootloader supplies the repository identity and routing, so you do not repeat the URL, ID, or protocol commands.

Examples:

- `@GitHub where were we on my project?`
- `@GitHub remember that I've decided to use option B.`
- `@GitHub update my current project status.`
- `@GitHub what do you currently have recorded about this?`

A generic explicit entry is also valid:

> `@GitHub Use my operational memory.`

Custom Instructions can tell ChatGPT when GitHub should be used, but they are not proof that the plugin actually ran. Repository retrieval or persistence should be claimed only when actual `@GitHub` actions provide the required evidence.

If setup cannot safely complete, ChatGPT should return **Operational memory: BLOCKED**, show one plain-language problem and one **Fix**, then ask you to say **`Retry setup.`** after fixing it. It should not dump repository IDs, blob details, or protocol jargon unless you ask.

See [`SETUP.md`](SETUP.md) for the exact bootloader shape plus advanced verification and troubleshooting.

## Development status

This template is currently **unreleased and in active development**. It is **not an acceptance candidate** and no release-candidate SHA is frozen. Substantive pre-release changes and advisory validation may continue normally. Acceptance begins only after an explicit maintainer decision changes `protocol_status` to `acceptance_candidate`; that transition commit is then the first SHA eligible to freeze under the acceptance gate in [`MIGRATIONS.md`](MIGRATIONS.md). The first real release identifier is assigned only after that gate passes.

## What the user experiences

The intended interface is the conversation, not the files.

A user activates the private repository once, copies the completed bootloader once, then works normally. Operational memory can matter in **two directions**: prior durable state may affect the current task, or the current conversation may create/change clear future-governing state that should persist. Either is a reason to engage `@GitHub` and enter through `START_HERE.md`.

That second trigger matters even when a conversation began with no need for repository context. A firm decision, status change, constraint, or durable correction that emerges later should still be routed and saved under the normal verification rules rather than being lost merely because GitHub was not needed at the beginning.

Explicit `@GitHub` is the dependable execution path. The bootloader removes repository-identity and routing complexity; it should not be treated as proof that a product surface actually invoked the plugin automatically.

The template also includes a **latent generic working companion** in [`COMPANION.md`](COMPANION.md). It supplies sensible fallback collaboration behavior for users who have not built their own companion or detailed Custom Instructions. It is not a named persona and must not replace, rename, rewrite, or compete with an existing user companion/persona/Custom Instructions. [`WORKING_STYLE.md`](WORKING_STYLE.md) can selectively calibrate that fallback as durable preferences emerge.

Projects may also link other GitHub repositories when ongoing work genuinely spans repositories. Operational Memory can retain the cross-session purpose, decisions, current context, and relationship between those repos while each linked repo remains authoritative for the content assigned to it, such as code, implementation docs, issues, or releases. Unrelated repos do not need to be registered, and registration is never treated as access permission.

If the user clearly changes something that should govern future work, such as a finalized decision or active project target, a conservative persistence watch can route and persist that change under normal verification rules without requiring a magic “remember this” phrase. Ambiguous, inferred, sensitive, or structurally novel persistence still requires confirmation.

Later, a fresh conversation can ask `@GitHub where were we?` and reconstruct the situation from explicit current state and active decisions rather than relying only on conversational recollection.

See [`EXAMPLE.md`](EXAMPLE.md) for a fictional before/after demonstration.

## How this fits with native ChatGPT memory

This repository complements native ChatGPT memory and conversation history; it does not replace them.

Native memory can continue providing useful conversational continuity. Operational Memory adds an **explicit authority layer** for the smaller subset of information where it matters to know what is current, what superseded what, where governing state lives, and whether a consequential change actually persisted.

A useful mental model is:

- **conversation** — normal working surface;
- **tools, files, and web sources** — evidence and execution when needed;
- **native ChatGPT memory** — continuity and personalization;
- **user companion / Custom Instructions** — any identity/style guidance the user already chose;
- **`COMPANION.md`** — generic fallback collaboration quality only where stronger user guidance is absent;
- **operational memory** — explicit state, decisions, durable knowledge, working preferences, project routing, and cross-repository relationships important enough to govern future work.

The repository should stay selective. It is not a transcript archive. If durable state cannot materially change the task and the conversation has not created a clear future-governing change, using no repository context is a valid route.

When sources conflict, the user's current instruction wins. Current verified operational state and active decisions can then serve as explicit authority rather than allowing older memory or recollection to quietly overrule them. `COMPANION.md` is behavioral fallback, not state authority.

## What changes in practice

| Situation | ChatGPT Plus without this repo | With this repo |
| --- | --- | --- |
| Fresh chat later | Prior context may be useful but its basis may be unclear. | ChatGPT can retrieve explicit durable state through a scoped front door. |
| “Where were we?” | Reconstruct from available chat/native context. | `@GitHub` retrieves current project/global state and active decisions. |
| Important decision changes | Old and new positions may coexist. | New decision can explicitly supersede the old one and reconcile current state. |
| Durable fact becomes stale | Freshness may be unclear. | Knowledge can carry verification/review metadata. |
| Repeated working preference | May need to be re-taught or depend on native personalization. | Explicit collaboration preferences can be stored selectively in `WORKING_STYLE.md`. |
| Starting collaboration quality | Default ChatGPT behavior plus existing personalization. | Adds a generic, non-persona companion baseline only where stronger user guidance is absent. |
| Existing companion/persona | Whatever the user has configured. | Keeps it. The generic companion must not overwrite or compete with it. |
| Several ongoing projects | Context can blur. | `PROJECTS.md` routes to the correct project front door. |
| Work spans several GitHub repos | Cross-repo context may be reconstructed ad hoc. | A project can link relevant repos by immutable ID while each repo remains canonical for its declared role. |
| Write claims success | No Git-style receipt is inherent to chat memory. | Consequential writes are reread and verified. |
| Concurrent/manual edit | Silent overwrite is possible in an unversioned store. | Current version/blob preconditions can reject stale writes. |
| Memory repository renamed | A name-based pointer may become stale. | The bootloader resolves the same GitHub repository ID to its new owner/name. |
| Linked repository renamed | Cross-repo references may become stale if name-based. | Project links use immutable repository IDs and resolve current owner/name at runtime. |
| Conversation creates a firm decision late | It may vanish with the chat. | The persistence trigger can engage operational memory even if prior state was not needed initially. |
| One-off casual question | Just chat. | Also just chat. No-repository-context is valid. |

The practical difference is not **“ChatGPT remembers more.”** It is:

**For information important enough to govern ongoing work, the user can inspect what is current, what was superseded, where it belongs, how related repositories fit together, and whether changes actually persisted.**

For the shorter human version of this comparison, see [`WHAT_TO_EXPECT.md`](WHAT_TO_EXPECT.md).

## Architecture

```text
                     COMPANION.md
                  generic fallback only
                          |
START_HERE.md ------------+
    |
    +-- global state
    |      CURRENT.md
    |      DECISIONS.md
    |      KNOWLEDGE.md
    |      WORKING_STYLE.md
    |
    +-- project router
           PROJECTS.md
              |
              +-- projects/<slug>/PROJECT.md
                       |
                       +-- CURRENT.md
                       +-- DECISIONS.md
                       +-- KNOWLEDGE.md
                       +-- optional linked GitHub repositories
                           (immutable repository ID + role + authority)
```

`PROTOCOL.yaml` is the machine-readable manifest. `START_HERE.md` is the runtime front door. Detailed procedures live in `OPERATIONS.md` so normal sessions do not need to load the whole protocol library.

Git history preserves evolution, but **Git history is not current authority**.

## The bootloader principle

Persistent ChatGPT instructions should be tiny. Activation obtains the working repository's stable numeric GitHub repository ID, inserts it into the compact bootloader defined by `PROTOCOL.yaml`, and gives the completed block to the user.

The user pastes that block **at the top of Custom Instructions without replacing existing instructions**. The user does not need to understand or manually manage the ID. ChatGPT uses it internally so an ordinary repository rename does **not** require editing the bootloader or migrating durable state.

The bootloader carries two triggers: use operational memory when prior durable state may materially affect the task **or** when the conversation creates/changes clear future-governing state that should persist. On actual GitHub invocation, ChatGPT resolves the ID to the repository's current owner/name and retrieves `START_HERE.md`.

The bootloader itself is not evidence that `@GitHub` ran. Explicit `@GitHub` is the dependable repository-backed path; if the plugin was not actually engaged, ChatGPT should not claim repository retrieval or persistence.

If the ID cannot be resolved, ChatGPT should fail visibly rather than guess a similarly named repository.

For users who skip Custom Instructions, the simple manual fallback is:

> `@GitHub Use operational memory from <YOUR REPOSITORY URL>.`

Repository resolution and front-door entry are internal steps, not user commands.

## Controlled persistence

Before writing durable material, the protocol routes it to an existing source of record, global current state, a durable decision, durable knowledge, working style, the correct registered project, or `UNROUTED / no legitimate home`.

If a project registers a linked repository as canonical for a specific role, material belonging to that role stays there rather than being copied into Operational Memory merely for convenience.

The system should not automatically persist brainstorming, discarded alternatives, casual conversation, one-off preferences, or sensitive material merely because it could be useful later.

Working style is for collaboration preferences, not biography or psychological profiling, and it may not suppress honest evaluation, correction, or material risk flagging.

## Verification and failure posture

For consequential writes, the basic closed loop is:

`read -> authorized/routed write -> reread -> verify intended state`

Multi-file changes use a write-set with an explicit postcondition. Tool acknowledgement alone is not proof that the intended durable state exists.

The preferred failure behavior is **closed, loud, and recoverable**. During setup that is deliberately translated into a lay-user response: **BLOCKED → one problem → one Fix → Retry setup.** Technical diagnostics remain available when requested.

The repository also includes an advisory deterministic validator for structural invariants. It does not pretend to validate semantic truth, correct routing, prompt-injection safety, or model behavior.

## Supported OpenAI surfaces

### ChatGPT Chat

The supported lay-user baseline is **ChatGPT Plus (currently $20/month) or higher**. **Free and ChatGPT Go are unsupported.** In addition, the `@GitHub` plugin must be installed/selected, authenticated to GitHub, authorized for the exact private working repository, and expose repository read/write actions.

A supported plan is necessary but not sufficient. Plugin availability and actions can vary by account, workspace, role, region, surface, and rollout, so activation verifies the actual capability. A visible plugin listing or a separate read-only GitHub connection does not satisfy this persistence protocol.

OpenAI separately documents a GitHub app/connection used for repository search and analysis as read-only. That surface can support retrieval but cannot satisfy this persistence protocol. Do not generalize its read-only limitation to the selected `@GitHub` plugin; `SETUP.md` uses actual exposed actions plus reversible CRUD/readback to determine readiness.

For repository-backed work, explicit `@GitHub` is the dependable execution path. Custom Instructions provide the stable repository identity and tell ChatGPT when the plugin should be used, but this protocol does not assume those instructions can deterministically force plugin invocation on every ChatGPT surface.

### Codex

The repository includes a tiny root `AGENTS.md` bootloader. Codex enters through the same `PROTOCOL.yaml` and `START_HERE.md`; it should not create a competing Codex-specific memory structure.

### ChatGPT Work

When equivalent write-capable GitHub actions are available in Work on a supported plan/workspace, the same repository and front door apply. Longer multi-step execution does not weaken persistence authorization, routing, privacy, write-set, or readback rules.

### Other models

The Markdown protocol is intentionally portable. Other models may be able to use it when their normal interface provides equivalent persistent bootstrapping plus scoped GitHub read/write capability. This release does not add speculative provider-specific machinery.

## Privacy and recovery boundaries

Use a **private** working repository. Do not store passwords, tokens, private keys, recovery codes, full payment/bank information, or similar secrets.

A private GitHub repository is private on GitHub, but content retrieved into ChatGPT enters the ChatGPT processing path under the applicable product settings and terms.

Git history is useful recovery evidence but is not an independent backup of the GitHub account/repository itself. If losing the operational-memory repository would be materially costly, keep an independent clone/archive using a backup practice you trust.

See [`SECURITY.md`](SECURITY.md) for details and [`DISCLAIMER.md`](DISCLAIMER.md) for project and third-party boundaries.

## Structural validation and behavioral evals

Two different test surfaces are included:

- `tools/validate_protocol.py` checks machine-verifiable structural invariants and soft warning budgets.
- `EVALS.md` defines adversarial scenarios for model-mediated behavior, including routing, authority, false retrieval/write claims, over-persistence, activation, GitHub surface selection, onboarding failure recovery, late-conversation persistence activation, repository identity/rename behavior, cross-repository authority/permission behavior, companion precedence, working-style safety, compatibility, and maintenance failures.

The included GitHub Actions workflow is advisory. In a derived working copy it runs after every push to canonical `main` (including normal Operational Memory writes), for pull requests, or when manually dispatched. Each run checks out the repository on a GitHub-hosted runner with `contents: read`, installs pinned `PyYAML==6.0.2`, runs validator regression self-tests and structural validation, and does not replace the immediate write/readback verification required before claiming persistence.

`EVAL_RESULTS.md` is the results ledger. It deliberately distinguishes a structural validator PASS from behavioral evidence. No qualifying independent behavioral run is claimed until one is actually performed.

## Feedback and contributions

- **GitHub Discussions**: questions, usage experiences, early ideas, experiments, and show-and-tell.
- **GitHub Issues**: reproducible bugs, setup failures, confusing behavior, and actionable improvements.
- **Pull Requests**: concrete proposed changes.
- **Private contact**: `contact@referencefield.com`.

Do not post credentials, private repository contents, or sensitive personal information in public feedback channels.

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Repository map

- `README.md` — product overview and beginner start
- `WHAT_TO_EXPECT.md` — short human-facing install/value guide
- `SETUP.md` — beginner setup plus advanced verification/troubleshooting
- `START_HERE.md` — compact runtime authority/front door
- `PROTOCOL.yaml` — machine-readable protocol and compatibility manifest
- `COMPANION.md` — generic fallback collaboration baseline; never replaces an existing user companion
- `AGENTS.md` — Codex bootloader
- `OPERATIONS.md` — project creation, write-sets, health, recovery, maintenance
- `SECURITY.md` — privacy, secrets, recovery boundaries, optional Git hardening
- `DISCLAIMER.md` — project independence, warranty/reliability boundaries, and user responsibility
- `MIGRATIONS.md` — release/update rules and controlled release cleanup
- `EXAMPLE.md` — fictional worked example
- `EVALS.md` — adversarial behavioral scenarios
- `EVAL_RESULTS.md` — behavioral-results ledger
- `CONTRIBUTING.md` — contribution routes and design guardrails
- `CURRENT.md`, `DECISIONS.md`, `KNOWLEDGE.md`, `WORKING_STYLE.md` — global durable state
- `PROJECTS.md` — project registry/router
- `projects/_TEMPLATE/` — project skeleton, including optional linked-repository registration
- `tools/` — advisory structural validator
- `.github/` — contribution forms and advisory validation workflow

## Prior art and positioning

This project grew out of long-running ChatGPT + GitHub operational work at **Reference Field, Inc.** It does **not** claim novelty for Git-backed memory, Markdown state, durable decision logs, supersession, repository-local AI instructions, retrieval-before-work, generic assistant behavior guidelines, or validation.

Repository-local AI instruction files are established prior art, including OpenAI Codex `AGENTS.md`, Anthropic Claude Code `CLAUDE.md`, and Cursor project rules. Neighboring or more infrastructure-heavy systems include Context Spine, Letta/MemFS, Agent Zero, ProjectMemory, context-repository, Supersede, and filesystem-based memory research.

This template's narrower proposition is a low-infrastructure, human-readable operational-memory layer for ordinary ChatGPT users who want conversational GitHub writeback, scoped routing, explicit supersession, cross-repository continuity, a non-destructive generic collaboration baseline, and post-write verification without first adopting an agent framework or database.

## Validation status and limits

The repository has undergone design review, adversarial review, prior-art comparison, deterministic structural validation, and live GitHub write/readback iteration.

**Longitudinal multi-user reliability has not yet been established.** Many semantically important safeguards remain instructions executed by ChatGPT rather than independently enforced controls.

This is not an infallible memory system, objective source of truth, deterministic control plane, background synchronization service, security boundary, or universal replacement for native ChatGPT memory/Projects.

It cannot know about changes that were never recorded, guarantee automatic plugin invocation, guarantee that a generic companion will dominate stronger user-provided guidance, or guarantee future product behavior.

Licensed under the MIT License. See [`LICENSE`](LICENSE). Additional practical limitations and third-party independence are described in [`DISCLAIMER.md`](DISCLAIMER.md).

Created by **Reference Field, Inc.** · https://referencefield.com · contact@referencefield.com