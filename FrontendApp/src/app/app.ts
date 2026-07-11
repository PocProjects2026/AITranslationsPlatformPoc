import { Component, signal } from '@angular/core';

@Component({
  selector: 'app-root',
  imports: [],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly pendingCount = signal(2);
  protected readonly selectedLocale = signal('en');

  protected addPendingTranslation(): void {
    this.pendingCount.update((count) => count + 1);
  }

  protected selectLocale(event: Event): void {
    this.selectedLocale.set((event.target as HTMLSelectElement).value);
  }
}
