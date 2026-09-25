# Contributing

Thank you for helping improve Reference Field Operational Memory.

The project is intentionally narrow: a low-infrastructure, lay-user-friendly way to give ChatGPT explicit, user-owned operational memory in GitHub without turning the repository into an uncontrolled knowledge base or requiring an agent framework.

## Where to contribute

Choose the lightest channel that fits:

- **GitHub Discussions** — questions, usage experiences, design ideas, experiments, and proposals that are not yet concrete changes.
- **GitHub Issues** — reproducible bugs, setup failures, confusing behavior, or a specific improvement that needs tracking.
- **Pull Requests** — concrete changes you are ready to propose to the public template. You do not need to open an issue first.
- **Private contact** — `contact@referencefield.com` for matters that should not be public.

Do not post secrets, private repository contents, credentials, or sensitive personal information in Discussions, Issues, or Pull Requests.

## What fits this project

Strong proposals usually preserve these principles:

- ordinary ChatGPT users should not need a terminal for normal operation;
- the supported ChatGPT baseline is **Plus or higher**; Free and ChatGPT Go are unsupported by this release;
- the primary ChatGPT path requires `@GitHub` to be installed/selected, authenticated to GitHub, authorized for the exact repository, and exposing repository read/write actions, with explicit `@GitHub` invocation when needed;
- durable material is routed before it is written;
- existing sources of record are preferred over new files;
- project boundaries prevent global files from becoming junk drawers;
- persistence is selective rather than transcript-like;
- consequential writes are reread and verified;
- multi-file changes use a write-set and verified postcondition;
- uncertainty fails visibly rather than becoming authoritative state;
- structural complexity must earn its place;
- the system should remain human-readable and user-owned.

## Before proposing a new file or subsystem

A new durable home should pass the same promotion test used by the protocol:

1. it has a distinct role not served by an existing source;
2. the need is recurring rather than one-off;
3. a future session has a clear trigger for retrieving it;
4. its authority is defined;
5. it is reachable from an existing front door/index;
6. the user can see that the structure expanded;
7. required topology changes are reflected in `PROTOCOL.yaml` and release/migration guidance.

If those conditions are not met, prefer improving an existing route instead of adding another file.

## Pull request expectations

A useful pull request should explain:

- the user failure mode or opportunity it addresses;
- why the change belongs in this low-infrastructure template;
- whether it changes routing, persistence, authority, privacy, or repository topology;
- whether `EVALS.md` needs a new or changed adversarial scenario;
- whether `tools/validate_protocol.py` needs a deterministic structural check;
- whether private working copies would require a migration after a public release.

Run the advisory validator when changing protocol structure:

`python tools/validate_protocol.py`

The validator is structural. A green result does not replace semantic review.

## Compatibility contributions

The primary release target is **ChatGPT Plus or higher** using the authenticated **write-capable `@GitHub` plugin/app path** described in `SETUP.md`. Free and ChatGPT Go are outside this release's support boundary. A read-only GitHub connection may support retrieval but cannot satisfy the persistence requirements.

The repository also includes a minimal root `AGENTS.md` bootloader so OpenAI Codex can enter through the same `START_HERE.md` protocol instead of inventing a second operating model. ChatGPT Work should use the same repository and front door when equivalent GitHub write actions are available on a supported plan/workspace.

Changes for other model providers are welcome when they preserve the same user-facing simplicity and can demonstrate equivalent repository read/write behavior, scoped retrieval, and persistent bootstrapping. Do not add provider-specific machinery to the default path merely for theoretical compatibility.

## Contact

For private questions or feedback: `contact@referencefield.com`.
