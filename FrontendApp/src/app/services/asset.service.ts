import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  Asset,
  AssetCreate,
  AssetUpdate,
} from '../models/asset';

@Injectable({
  providedIn: 'root',
})
export class AssetService {
  private readonly http = inject(HttpClient);

  private readonly apiUrl =
    'https://aitranslationsplatformpoc.onrender.com';

  getAssets(): Observable<Asset[]> {
    return this.http.get<Asset[]>(
      `${this.apiUrl}/assets`
    );
  }

  createAsset(asset: AssetCreate): Observable<Asset> {
    return this.http.post<Asset>(
      `${this.apiUrl}/assets`,
      asset
    );
  }

  updateAsset(
    id: number,
    asset: AssetUpdate
  ): Observable<Asset> {
    return this.http.patch<Asset>(
      `${this.apiUrl}/assets/${id}`,
      asset
    );
  }

  deleteAsset(id: number): Observable<void> {
    return this.http.delete<void>(
      `${this.apiUrl}/assets/${id}`
    );
  }
}