# Free Resources Recommendations

Last reviewed: 2026-07-12

This document identifies practical free resources for the first release of the
platform. Free tiers can change, so confirm their current limits before creating
an account. Do not send confidential production content to an external translation
provider until data governance approves the provider, region, and retention terms.

## Recommended POC Deployment

| Need | Recommended service | Free capability | POC limitation | Portability rule |
| --- | --- | --- | --- | --- |
| Angular frontend | Cloudflare Pages | Static hosting and GitHub deployments; 500 builds per month | Cloudflare-specific deployment settings | Build a static Angular distribution; keep the API URL in environment configuration |
| Translation API | Render Free Web Service | GitHub deployment for Python or Docker services | Sleeps after 15 minutes of inactivity; filesystem is ephemeral | Run `TranslationService` from a Docker image and persist no state on disk |
| Translation database | Supabase Free Postgres | 500 MB PostgreSQL database | Project pauses after one week of inactivity | Access only through PostgreSQL and `DATABASE_URL`; do not use Supabase-only APIs |
| CI/CD | GitHub Actions | 2,000 minutes/month for a GitHub Free organization with private repositories | Monthly quota for private repositories | Keep build, test, and Docker build workflows in GitHub Actions |
| Generated translation artifacts | PostgreSQL during the POC | Stores small XLIFF and JSON artifacts with their version and metadata | Not appropriate for large files at scale | Hide storage behind an `ArtifactStore` interface for future S3 or Azure Blob support |

## Translation Provider Options

| Provider | Free capability | Recommended use | Main constraint |
| --- | --- | --- | --- |
| DeepL API Free | 500,000 characters per month | Default external provider for the POC, especially English, French, and German | External service; free quota must be monitored |
| Azure AI Translator F0 | Up to 2 million characters per month | Preferred external provider when the future target is Azure | Requires an Azure subscription and data-governance approval |
| Amazon Translate | 2 million characters per month for the first 12 months | Alternative when AWS is already approved | Free period expires after 12 months |
| LibreTranslate | Self-hosted and open source | Option when translation data must not leave a controlled environment | Requires a hosted Docker service, language models, and AGPL license review |
| Fake provider | No external calls | Unit tests, CI, and local development | Produces test fixtures only; does not translate content |

## Provider Independence

`TranslationService` must keep the same internal contract regardless of provider.

| Concern | Required rule |
| --- | --- |
| Configuration | Select the provider with `TRANSLATION_PROVIDER=deepl`, `azure`, `aws`, `libretranslate`, or `fake`. |
| Application code | Implement each provider behind one `TranslationProvider` interface. |
| Quality checks | Run placeholder validation, glossary validation, similarity scoring, length checks, and ranking after every provider response. |
| CI | Use only the fake provider. CI must not spend translation quota or use a real API key. |
| Auditability | Store provider name, provider model or version where available, request character count, score, and artifact version. |
| Future migration | Keep the API in Docker, use PostgreSQL, and use environment variables rather than provider SDKs outside the adapter. |

## Team Decision

Use **Cloudflare Pages + Render + Supabase + GitHub Actions** for the deployed POC.
Use **DeepL API Free** as the initial external translation provider, with a fake provider
for CI. Switch to Azure AI Translator if Azure is selected as the target cloud. Use
LibreTranslate only when a self-hosted translation engine is required and the hosting
and license implications have been accepted.

## Sources

- [Cloudflare Pages limits](https://developers.cloudflare.com/pages/platform/limits/)
- [Render Free service limits](https://render.com/docs/free)
- [Supabase pricing](https://supabase.com/pricing)
- [GitHub Free pricing](https://github.com/pricing)
- [DeepL API Free limits](https://developers.deepl.com/docs/resources/usage-limits)
- [Azure AI Translator F0 reference](https://learn.microsoft.com/en-us/samples/azure/azure-quickstart-templates/cognitive-services-translate/)
- [Amazon Translate pricing](https://aws.amazon.com/translate/pricing/)
- [LibreTranslate](https://github.com/LibreTranslate/LibreTranslate)
