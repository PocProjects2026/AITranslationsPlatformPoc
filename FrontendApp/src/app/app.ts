import {
  Component,
  inject,
  LOCALE_ID,
  OnInit,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';

import {
  Asset,
  AssetCreate,
  AssetUpdate,
} from './models/asset';

import { AssetService } from './services/asset.service';

type SupportedLocale = 'en' | 'fr' | 'de';

export function getLocalizedPath(
  locale: SupportedLocale
): string {
  return locale === 'en' ? '/' : `/${locale}/`;
}

@Component({
  selector: 'app-root',
  imports: [FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {
  private readonly localeId = inject(LOCALE_ID);
  private readonly assetService = inject(AssetService);

  protected readonly localizedVersionCount = 3;

  protected readonly currentLocale =
    this.normalizeLocale(this.localeId);

  protected readonly assets = signal<Asset[]>([]);
  protected readonly assetsLoading = signal(false);
  protected readonly assetsError =
    signal<string | null>(null);

  protected readonly formSuccess =
    signal<string | null>(null);

  protected readonly formError =
    signal<string | null>(null);

  protected editingAssetId: number | null = null;

  protected assetName = '';
  protected assetReference = '';
  protected assetStatus = 'Active';
  protected assetOwner = '';
  protected assetTags = '';

  ngOnInit(): void {
    this.loadAssets();
  }

  protected changeLanguage(event: Event): void {
    const selectElement =
      event.target as HTMLSelectElement;

    const locale =
      selectElement.value as SupportedLocale;

    window.location.assign(
      getLocalizedPath(locale)
    );
  }

  protected loadAssets(): void {
    this.assetsLoading.set(true);
    this.assetsError.set(null);

    this.assetService.getAssets().subscribe({
      next: (assets) => {
        this.assets.set(assets);
        this.assetsLoading.set(false);
      },

      error: () => {
        this.assetsError.set(
          'Unable to load assets.'
        );

        this.assetsLoading.set(false);
      },
    });
  }

  protected submitAsset(): void {
    this.formSuccess.set(null);
    this.formError.set(null);

    const tags = this.assetTags
      .split(',')
      .map((tag) => tag.trim())
      .filter((tag) => tag.length > 0);

    if (this.editingAssetId === null) {
      const asset: AssetCreate = {
        name: this.assetName.trim(),
        reference: this.assetReference.trim(),
        status: this.assetStatus,
        owner: this.assetOwner.trim() || null,
        tags,
      };

      this.assetService.createAsset(asset).subscribe({
        next: () => {
          this.formSuccess.set(
            'Asset created successfully.'
          );

          this.resetForm();
          this.loadAssets();
        },

        error: (error) => {
          if (error.status === 409) {
            this.formError.set(
              'An asset with this reference already exists.'
            );
            return;
          }

          this.formError.set(
            'Unable to create asset.'
          );
        },
      });

      return;
    }

    const asset: AssetUpdate = {
      name: this.assetName.trim(),
      reference: this.assetReference.trim(),
      status: this.assetStatus,
      owner: this.assetOwner.trim() || null,
      tags,
    };

    this.assetService
      .updateAsset(this.editingAssetId, asset)
      .subscribe({
        next: () => {
          this.formSuccess.set(
            'Asset updated successfully.'
          );

          this.resetForm();
          this.loadAssets();
        },

        error: (error) => {
          if (error.status === 409) {
            this.formError.set(
              'An asset with this reference already exists.'
            );
            return;
          }

          this.formError.set(
            'Unable to update asset.'
          );
        },
      });
  }

  protected startEdit(asset: Asset): void {
    this.editingAssetId = asset.id;

    this.assetName = asset.name;
    this.assetReference = asset.reference;
    this.assetStatus = asset.status;
    this.assetOwner = asset.owner ?? '';

    this.assetTags = asset.tags
      .map((tag) => tag.name)
      .join(', ');

    this.formSuccess.set(null);
    this.formError.set(null);
  }

  protected deleteAsset(asset: Asset): void {
    const confirmed = window.confirm(
      `Delete "${asset.name}"?`
    );

    if (!confirmed) {
      return;
    }

    this.assetService.deleteAsset(asset.id).subscribe({
      next: () => {
        if (this.editingAssetId === asset.id) {
          this.resetForm();
        }

        this.loadAssets();
      },

      error: () => {
        this.assetsError.set(
          'Unable to delete asset.'
        );
      },
    });
  }

  protected resetForm(): void {
    this.editingAssetId = null;

    this.assetName = '';
    this.assetReference = '';
    this.assetStatus = 'Active';
    this.assetOwner = '';
    this.assetTags = '';

    this.formError.set(null);
  }

  private normalizeLocale(
    localeId: string
  ): SupportedLocale {
    const locale = localeId.split('-')[0];

    if (locale === 'fr' || locale === 'de') {
      return locale;
    }

    return 'en';
  }
}