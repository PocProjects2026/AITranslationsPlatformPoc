import json
from pathlib import Path

from app.services.pdf_generator import generate_asset_management_report

SUPPORTED_LANGUAGES = {"en", "fr", "de"}

LANGUAGE = "de"

SERVICE_ROOT = Path(__file__).resolve().parents[1]

TRANSLATION_FILE = (
    SERVICE_ROOT
    / "app"
    / "translations"
    / f"messages.{LANGUAGE}.json"
)

OUTPUT_FILE = (
    SERVICE_ROOT
    / "generated-reports"
    / f"sample-report-{LANGUAGE}.pdf"
)


def main() -> None:
    if LANGUAGE not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language: {LANGUAGE}. "
            f"Supported languages: en, fr, de."
        )
    with TRANSLATION_FILE.open(
        mode="r",
        encoding="utf-8",
    ) as translation_file:
        translations = json.load(translation_file)
  
    
        generated_file = generate_asset_management_report(
            output_path=OUTPUT_FILE,
            report_title=translations[
                "asset-management-report-title"
            ],
            report_description=translations[
                "asset-management-report-description"
            ],
            total_assets_label=translations[
                "asset-management-total-assets"
            ],
            total_assets=3,
            status_label=translations[
                "asset-management-status"
            ],
            completed_status=translations[
                "asset-management-status-completed"
            ],
)
    

    print(
        f"PDF generated successfully: "
        f"{generated_file}"
    )


if __name__ == "__main__":
    main()