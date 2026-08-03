from pathlib import Path

from app.services.pdf_generator import generate_sample_pdf


# Représente la racine du dossier AssetManagementService.
SERVICE_ROOT = Path(__file__).resolve().parents[1]

# Définit l'emplacement du PDF qui sera généré.
OUTPUT_FILE = (
    SERVICE_ROOT
    / "generated-reports"
    / "sample-report.pdf"
)


def main() -> None:
    generated_file = generate_sample_pdf(OUTPUT_FILE)

    print(
        f"PDF generated successfully: "
        f"{generated_file}"
    )


if __name__ == "__main__":
    main()