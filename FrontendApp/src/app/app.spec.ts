import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { vi } from 'vitest';

import { App, getLocalizedPath } from './app';
import { AssetService } from './services/asset.service';

describe('App', () => {
  const assetServiceMock = {
    getAssets: vi.fn(() =>
      of([
        {
          id: 1,
          name: 'Test Server',
          reference: 'TEST-001',
          status: 'Active',
          owner: 'Platform Team',
          tags: [
            {
              id: 1,
              name: 'Test',
            },
          ],
        },
      ]),
    ),

    createAsset: vi.fn(() =>
      of({
        id: 2,
        name: 'New Server',
        reference: 'NEW-001',
        status: 'Active',
        owner: 'Platform Team',
        tags: [],
      }),
    ),

    updateAsset: vi.fn(() =>
      of({
        id: 1,
        name: 'Updated Server',
        reference: 'TEST-001',
        status: 'Active',
        owner: 'Platform Team',
        tags: [],
      }),
    ),

    deleteAsset: vi.fn(() => of(undefined)),

    generateReport: vi.fn(() =>
      of(new Blob(['pdf'], { type: 'application/pdf' })),
    ),
  };

  beforeEach(async () => {
    vi.clearAllMocks();

    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        {
          provide: AssetService,
          useValue: assetServiceMock,
        },
      ],
    }).compileComponents();
  });

  it('should create the application', () => {
    const fixture = TestBed.createComponent(App);

    expect(fixture.componentInstance).toBeTruthy();
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

  it('should render the asset name label and placeholder', () => {
    const fixture = TestBed.createComponent(App);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;

    const label = compiled.querySelector(
      'label[for="asset-name"]',
    ) as HTMLLabelElement | null;

    const input = compiled.querySelector(
      '#asset-name',
    ) as HTMLInputElement | null;

    expect(normalizeText(label?.textContent)).toBe('Asset name');

    expect(input?.placeholder).toBe(
      'Example: Web Server',
    );
  });

  it('should provide English, French and German language options', () => {
    const fixture = TestBed.createComponent(App);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;

    const select = compiled.querySelector(
      '#application-language',
    ) as HTMLSelectElement | null;

    expect(select).not.toBeNull();

    const options = Array.from(
      select?.options ?? [],
    ).map((option) => ({
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

  it('should load assets from the AssetService', () => {
    const fixture = TestBed.createComponent(App);

    fixture.detectChanges();

    expect(assetServiceMock.getAssets).toHaveBeenCalled();

    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.textContent).toContain(
      'Test Server',
    );

    expect(compiled.textContent).toContain(
      'TEST-001',
    );

    expect(compiled.textContent).toContain(
      'Platform Team',
    );
  });

  it('should render edit and delete actions for an asset', () => {
    const fixture = TestBed.createComponent(App);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;

    const buttons = Array.from(
      compiled.querySelectorAll('button'),
    ).map((button) =>
      normalizeText(button.textContent),
    );

    expect(buttons).toContain('Edit');
    expect(buttons).toContain('Delete');
  });

  it('should render the PDF report generation section', () => {
    const fixture = TestBed.createComponent(App);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.textContent).toContain(
      'Generate Asset Report',
    );

    expect(compiled.textContent).toContain(
      'Generate PDF',
    );
  });
});

/**
 * Removes indentation, line breaks and repeated spaces
 * from rendered text.
 */
function normalizeText(
  value: string | null | undefined,
): string {
  return value?.replace(/\s+/g, ' ').trim() ?? '';
}