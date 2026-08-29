export interface Tag {
  id: number;
  name: string;
}

export interface Asset {
  id: number;
  name: string;
  reference: string;
  status: string;
  owner: string | null;
  tags: Tag[];
}

export interface AssetCreate {
  name: string;
  reference: string;
  status: string;
  owner?: string | null;
  tags: string[];
}

export interface AssetUpdate {
  name?: string;
  reference?: string;
  status?: string;
  owner?: string | null;
  tags?: string[];
}