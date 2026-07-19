import { TestBed } from '@angular/core/testing';

import { App, getLocalizedPath } from './app';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
    }).compileComponents();
  });

  it('should create the application', () => {
    const fixture = TestBed.createComponent(App);
    const component = fixture.componentInstance;

    expect(component).toBeTruthy();
  });

  it('should render the main localized interface content', () => {
    const fixture = TestBed.createComponent(App);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const heading = compiled.querySelector('h1');
    const versionMessage = compiled.querySelector('.version-message');

    expect(normalizeText(heading?.textContent)).toBe(
      'One interface, three languages.',
    );

    expect(normalizeText(versionMessage?.textContent)).toBe(
      'Available in 3 languages',
    );
  });

  it('should render a representative label and placeholder', () => {
    const fixture = TestBed.createComponent(App);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const label = compiled.querySelector(
      'label[for="product-name"]',
    ) as HTMLLabelElement | null;
    const input = compiled.querySelector(
      '#product-name',
    ) as HTMLInputElement | null;

    expect(normalizeText(label?.textContent)).toBe('Product name');
    expect(input?.placeholder).toBe('Enter a product name');
  });

  it('should provide English, French and German language options', () => {
    const fixture = TestBed.createComponent(App);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const select = compiled.querySelector(
      '#application-language',
    ) as HTMLSelectElement | null;

    expect(select).not.toBeNull();

    const options = Array.from(select?.options ?? []).map((option) => ({
      value: option.value,
      label: normalizeText(option.textContent),
    }));

    expect(options).toEqual([
      {
        value: 'en',
        label: 'English',
      },
      {
        value: 'fr',
        label: 'French',
      },
      {
        value: 'de',
        label: 'German',
      },
    ]);

    expect(select?.value).toBe('en');
  });

  it('should map each locale to its localized application path', () => {
    expect(getLocalizedPath('en')).toBe('/');
    expect(getLocalizedPath('fr')).toBe('/fr/');
    expect(getLocalizedPath('de')).toBe('/de/');
  });

  it('should display a success message after saving a product', () => {
    const fixture = TestBed.createComponent(App);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const saveButton = compiled.querySelector(
      '.button--primary',
    ) as HTMLButtonElement | null;

    expect(saveButton).not.toBeNull();

    saveButton?.click();
    fixture.detectChanges();

    const feedback = compiled.querySelector('.feedback--success');

    expect(normalizeText(feedback?.textContent)).toBe(
      'Product saved successfully.',
    );
  });

  it('should display a deletion message after deleting a product', () => {
    const fixture = TestBed.createComponent(App);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const deleteButton = compiled.querySelector(
      '.button--danger',
    ) as HTMLButtonElement | null;

    expect(deleteButton).not.toBeNull();

    deleteButton?.click();
    fixture.detectChanges();

    const feedback = compiled.querySelector('.feedback--deleted');

    expect(normalizeText(feedback?.textContent)).toBe(
      'Product deleted successfully.',
    );
  });
});

/**
 * Removes indentation, line breaks and repeated spaces from rendered text.
 */
function normalizeText(value: string | null | undefined): string {
  return value?.replace(/\s+/g, ' ').trim() ?? '';
}