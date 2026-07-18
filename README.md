# AITranslationsPlatformPoc

Single repository for the first implementation of the AI translation platform.

## Structure

- `FrontendApp/`: Angular application using XLIFF source and localized files.
- `TranslationService/`: Python API for translating, validating, ranking, and packaging artifacts.

ReportService and AssetManagementService will consume the translation artifacts but are
not created in this first foundation. Their integration contracts will be added with
their user stories.

## Working agreement

`main` is the shared baseline. Contributors branch from `develop`, link each pull
request to its user story, and include test evidence. CI/CD definitions are intentionally
not part of this first skeleton because they have separate GitHub Project stories.
