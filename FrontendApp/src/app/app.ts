import { Component, inject, LOCALE_ID, signal } from '@angular/core';

type SupportedLocale = 'en' | 'fr' | 'de';
type FeedbackMessage = 'saved' | 'deleted' | null;


export function getLocalizedPath(locale: SupportedLocale): string {
  return locale === 'en' ? '/' : `/${locale}/`;
}

@Component({
  selector: 'app-root',
  imports: [],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  private readonly localeId = inject(LOCALE_ID);

  protected readonly localizedVersionCount = 3;

  protected readonly feedback = signal<FeedbackMessage>(null);

  protected readonly currentLocale = this.normalizeLocale(this.localeId);

  protected changeLanguage(event: Event): void {
    const selectElement = event.target as HTMLSelectElement;
    const locale = selectElement.value as SupportedLocale;

    window.location.assign(getLocalizedPath(locale));
  }

  protected saveProduct(): void {
    this.feedback.set('saved');
  }

  protected deleteProduct(): void {
    this.feedback.set('deleted');
  }
  protected cancelProduct(): void {
    this.feedback.set(null);
  }

  private normalizeLocale(localeId: string): SupportedLocale {
    const locale = localeId.split('-')[0];

    if (locale === 'fr' || locale === 'de') {
      return locale;
    }

    return 'en';
  }
}