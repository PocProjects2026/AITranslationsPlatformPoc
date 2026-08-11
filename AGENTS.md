# Working Agreement for Coding Agents

This repository is a learning-oriented POC with production-quality foundations. Changes
must remain easy for the project lead to read, judge, discuss, and approve.

## Primary Rule: Keep Changes Small

- Work on one review concern at a time.
- A normal change should cover one behavior, one architectural decision, or one
  delivery concern in one component.
- Do not combine application code, translation contracts, Docker, CI workflows, CD,
  and infrastructure in one change unless the project lead explicitly approves that
  scope.
- Prefer a change that can be understood and reviewed in 10 to 15 minutes.
- When additional work is discovered, record it as a follow-up instead of silently
  expanding the current change.
- Stop after completing the approved slice. Explain the result and wait before moving
  to the next slice.

## Before Editing

1. Inspect the relevant existing files and established patterns.
2. State the single objective of the proposed change.
3. Identify the files or areas likely to change.
4. State how the change will be verified.
5. If the request contains multiple concerns, propose an ordered sequence and implement
   only the first approved concern.

Do not create broad foundations, multiple workflows, deployment configuration, and IaC
in one pass merely because they may eventually be needed.

## Review Handoff

After every slice, provide a short handoff containing:

- What changed and why.
- The important files changed.
- Observable behavior or contract changes.
- Verification performed and its result.
- Decisions or risks that still require discussion.
- The proposed next small step.

Avoid large unexplained diffs. Use clear names, straightforward code, and short
documentation close to the behavior it describes.

## Git Workflow

- `develop` is the integration branch.
- `main` is the release branch.
- Use a feature or fix branch created from the current `origin/develop`.
- Deliver changes through pull requests.
- Keep commits focused on one review concern and use descriptive conventional commit
  messages.
- Do not include IDE state, build output, local secrets, or generated caches.
- Never discard unrelated user changes from a dirty working tree.

## CI/CD and Architecture Boundaries

- Keep every service independently buildable, versioned, and deployable.
- Use GitHub Actions as the primary CI/CD platform.
- Use GitHub Environments for environment configuration, approvals, secrets, and
  deployment history.
- Keep `develop` deployment and `main` release deployment separate.
- Release deployment from `main` is a separate manual action selecting an exact commit.
- Prevent conflicting deployments with workflow concurrency controls.
- Record application version, Git commit, image digest, and translation-artifact
  version together for deployment and rollback.
- Prefer Terraform for infrastructure as code unless a reviewed decision changes that
  direction.
- Prefer GitHub OIDC over long-lived credentials where the provider supports it.
- CI must run on clean hosted runners and must not depend on a developer machine.

Do not mix CI/CD or deployment work with translation algorithms, embeddings, candidate
ranking, or data-science changes in the same slice.

## Translation Artifacts

- The first POC may package assumed pre-generated sample translations while
  TranslationService publication is unavailable.
- Translation lock files, manifests, per-file checksums, and automated lock-update pull
  requests are deferred until the project lead explicitly approves that hardening step.
- When external translation artifacts are introduced, select an explicit version in
  the pipeline or environment configuration and record it with the deployment. Do not
  silently consume an untraceable `latest` version.
- Package the selected translation files into the application or image; do not download
  translations dynamically at application startup.
- Treat the application version and translation-artifact version as one reproducible
  deployment combination once versioned publication exists.

## Zero-Cost Requirement

- Paid technology is not allowed for this POC.
- Do not introduce paid plans, commercial runtime licenses, trials that become paid,
  or metered services that can generate charges.
- Prefer services that stop or fail when a free quota is exhausted rather than billing.
- Make any free-tier quota, sleep behavior, public-access limitation, or retention limit
  explicit before adoption.

## Security Baseline

- Grant GitHub Actions the minimum permissions required by each workflow.
- Pin third-party actions and container base images to immutable commits or digests.
- Keep credentials out of source, logs, workflow artifacts, and container images.
- Use synthetic or public POC test data because public endpoints currently have no
  application authentication.
- Add bounded request sizes, timeouts, rate limits, and health probes to public services.
- Fail closed when artifact validation, dependency restore, tests, or packaging fails.

## Verification

- Scale tests to the risk of the current slice.
- Run the narrowest relevant checks first, then the component build and tests.
- For CI changes, validate workflow structure and explain triggers, permissions,
  concurrency, and produced artifacts.
- For Docker changes, verify the image builds and the container starts as a non-root
  user before considering the slice complete.
- If a verification cannot be run, state that clearly; do not report the work as fully
  verified.
