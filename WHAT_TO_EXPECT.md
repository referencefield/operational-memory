# What to Expect

This page is for the person deciding whether Reference Field Operational Memory is worth installing.

## Short version

Use this if you have **ChatGPT Plus (currently $20/month) or a higher ChatGPT plan**, use ChatGPT for ongoing work, and can install/select and authenticate the **`@GitHub` plugin** with repository write actions.

**Free and ChatGPT Go are not supported by this release.** Seeing the Plugin Directory is not enough: the GitHub plugin must actually be available on your account/surface, authenticated to GitHub, authorized for the intended repository, and expose the required read/write actions.

This is useful when you regularly run into questions like:

- Where were we?
- Which decision is actually current?
- Did we already settle this?
- Why am I explaining the same project again?
- Did ChatGPT really save that change?
- How do several projects or GitHub repositories fit together?

Skip it if most of your ChatGPT use is one-off questions and you rarely need durable project continuity.

This does **not** make ChatGPT remember everything. It gives important ongoing state an explicit, user-owned place to live.

## What it should feel like

After one-time setup, normal use should still feel like ChatGPT, not like operating a database.

For dependable repository-backed work, start with `@GitHub`. A request can be as simple as:

`@GitHub where were we on Northstar?`

ChatGPT should find the configured memory repository, route to the relevant project, load only the state needed for the task, and answer from the current durable record.

When you make a clear future-governing change, such as finalizing a decision or changing an active target, Operational Memory can persist it under verification rules rather than requiring you to remember a special filing command.

You should also see a difference in **certainty about actions**. A tool saying “success” is not enough; consequential repository writes are reread and verified before ChatGPT claims they persisted.

## A competent starting companion, without replacing yours

The template includes `COMPANION.md`, a generic fallback for good collaboration: answer the real question, prefer accuracy over agreement, expose uncertainty, use tools deliberately, push back on material problems, verify consequential outputs, and produce usable results.

It is deliberately **not a named persona** and does not pretend to know you.

If you already have your own AI companion, persona, or Custom Instructions, Operational Memory does not replace or rewrite them. Your existing guidance remains in place; the generic companion fills only uncovered gaps. `WORKING_STYLE.md` can gradually preserve a small number of useful preferences that genuinely recur.

## ChatGPT Plus alone vs Operational Memory

| Situation | ChatGPT Plus out of the box | With Operational Memory |
| --- | --- | --- |
| Fresh chat later | Native memory/history may help, but the basis can be unclear or incomplete. | `@GitHub` can retrieve explicit current state and active decisions from a scoped durable source. |
| “Where were we?” | Reconstruct from available conversation/native context. | Route through the project registry and current project authority. |
| Important decision changes | Old and new positions can coexist in prior conversations. | New decisions can explicitly supersede old ones and update current state. |
| Durable fact becomes stale | Freshness may be hard to see. | Durable knowledge can carry verification and review metadata. |
| Repeated working preference | Native personalization may help, but the user may still repeat conventions. | Stable collaboration preferences can be selectively recorded in `WORKING_STYLE.md`. |
| Starting collaboration quality | Default ChatGPT behavior plus whatever personalization the user already has. | Adds a generic, non-persona companion baseline where stronger user guidance is absent. |
| Existing companion/persona | Whatever the user has already configured. | Keeps it. The generic companion must not overwrite or compete with it. |
| Several ongoing projects | Project boundaries can blur across chats. | `PROJECTS.md` routes each workstream through its own front door. |
| Work spans several GitHub repos | Each repo can be used separately, but cross-repo operating context may be reconstructed ad hoc. | One Operational Memory project can link relevant repos by immutable ID while leaving each repo authoritative for its own code/docs/issues/releases. |
| Write claims success | Conversation memory has no Git-style persistence receipt. | Consequential writes are reread and verified; real commit information is reported when available. |
| Concurrent/manual edit | There is no repository-version precondition in native memory. | Blob/version preconditions can reject stale writes and force reconciliation. |
| Memory repo renamed | A name-based instruction could go stale. | The bootloader resolves the same immutable GitHub repository ID after a rename. |
| Firm decision emerges late in a chat | It can remain only in that conversation unless separately saved. | A late persistence trigger can engage Operational Memory even when prior state was not needed at the start. |
| One-off casual question | Just chat. | Also just chat. No-repository-context is a valid route. |

The practical difference is not “more memory.” It is **more inspectable continuity and clearer authority for the information important enough to govern future work**.

## Multiple repositories

Your memory repository does not need to be your only GitHub repository.

If an ongoing project lives in another repository, Operational Memory can record that relationship using the other repository's immutable GitHub ID, role, and authority. For example, Operational Memory may own the project's cross-session context and decisions while the linked repository remains authoritative for source code and implementation documentation.

Unrelated repositories do not need to be registered. Knowing about a linked repository is also not permission to use it; actual `@GitHub` access is still required for each task.

## What this does not do

- It is not a background daemon or automatic synchronization service.
- It does not archive every conversation.
- It does not guarantee that Custom Instructions can force a plugin to run; explicit `@GitHub` is the dependable repository-backed path.
- It does not replace native ChatGPT memory or conversation history.
- It does not make model judgment deterministic or infallible.
- A `Review after` date does not create a reminder by itself.
- Linking another repository does not grant permission to read or modify it.
- It should not contain passwords, tokens, recovery codes, full financial credentials, or similar secrets.

## Setup cost

The supported release baseline is **ChatGPT Plus (currently $20/month) or higher**, an installed/selected and authenticated write-capable `@GitHub` plugin, and one private GitHub repository. Free and ChatGPT Go are unsupported.

The intended human setup is:

**Create → Connect → Activate → paste one compact Custom Instructions block.**

After that, you should not need to know repository IDs, protocol filenames, CRUD terminology, or Git internals.

If that sounds useful, continue with [`README.md`](README.md) or [`SETUP.md`](SETUP.md). For a concrete fictional example, see [`EXAMPLE.md`](EXAMPLE.md). For privacy and recovery boundaries, see [`SECURITY.md`](SECURITY.md).
