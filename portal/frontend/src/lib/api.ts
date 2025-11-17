export type SiteSearchParams = {
  text?: string;
  city?: string | null;
  province?: string | null;
  tags?: string[] | null;
  orderBy?: 'created_at' | 'name' | 'rating';
  orderDir?: 'asc' | 'desc';
  lat?: number | null;
  long?: number | null;
  radius?: number | null;
  page?: number;
  perPage?: number;
  favoritesOnly?: boolean;
};

export type HistoricSite = {
  id: number;
  name: string;
  brief_description?: string | null;
  city?: string | null;
  province?: string | null;
  state?: string | null;
  tags?: string[];
  cover_image_url?: string | null;
  rating?: number | null;
  created_at?: string;
  latitude?: number | null;
  longitude?: number | null;
  is_favorite?: boolean;
};

export type PaginatedResponse<T> = {
  items: T[];
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
};

export type FilterOptions = {
  cities: Array<{ id: number; name: string }>;
  provinces: Array<{ id: number; name: string }>;
  tags: Array<{ id: number; name: string; slug: string }>;
  states: Array<{ id: number; name: string }>;
};

const DEFAULT_PER_PAGE = 20;

function getApiBaseUrl(): string {
  const envUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/+$/, '');
  return envUrl ?? '/api';
}

function buildQuery(params: Record<string, unknown>): string {
  const qp = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return;
    if (Array.isArray(value)) {
      if (value.length === 0) return;
      qp.set(key, value.join(','));
    } else {
      qp.set(key, String(value));
    }
  });
  const s = qp.toString();
  return s ? `?${s}` : '';
}

function mapSiteFromBackend(s: any): HistoricSite {
  return {
    id: s.id,
    name: s.name,
    brief_description: s.brief_description ?? null,
    city: s.city ?? null,
    province: s.province ?? null,
    state: s.state_name ?? s.state ?? null,
    tags: Array.isArray(s.tags) 
      ? s.tags.map((t: any) => t.name ?? t.slug ?? String(t)) 
      : [],
    cover_image_url: s.cover_image_url ?? null,
    rating: s.rating ?? null,
    created_at: s.created_at,
    latitude: s.latitude ?? null,
    longitude: s.longitude ?? null,
    is_favorite: s.is_favorite ?? false,
  };
}

function mapOrderBy(orderBy?: SiteSearchParams['orderBy'], dir?: SiteSearchParams['orderDir']): string | undefined {
  if (!orderBy) return 'latest';
  const direction = dir || 'desc';
  if (orderBy === 'created_at') {
    return direction === 'asc' ? 'oldest' : 'latest';
  }
  if (orderBy === 'rating') {
    return direction === 'asc' ? 'rating-1-5' : 'rating-5-1';
  }
  return 'latest';
}

export async function fetchPublicSites(params: SiteSearchParams): Promise<PaginatedResponse<HistoricSite>> {
  const base = getApiBaseUrl();
  const query = buildQuery({
    name: params.text,
    description: params.text,
    city: params.city,
    province: params.province,
    tags: params.tags,
    order_by: mapOrderBy(params.orderBy, params.orderDir),
    lat: params.lat,
    long: params.long,
    radius: (params.lat != null && params.long != null && params.radius != null) 
      ? params.radius / 1000 
      : undefined,
    page: params.page ?? 1,
    per_page: params.perPage ?? DEFAULT_PER_PAGE,
  });
  const url = `${base}/sites${query}`;
  const res = await fetch(url, {
    headers: { 'Accept': 'application/json' },
    credentials: 'omit',
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Error al cargar sitios (${res.status}): ${text}`);
  }
  const raw = await res.json();
  const items: HistoricSite[] = (raw.sites || []).map(mapSiteFromBackend);
  const pagination = raw.pagination || {};
  return {
    items,
    page: pagination.page ?? 1,
    per_page: pagination.per_page ?? (params.perPage ?? DEFAULT_PER_PAGE),
    total: pagination.total ?? items.length,
    total_pages: pagination.pages ?? 1,
  };
}

export async function fetchMyFavorites(page = 1, perPage = DEFAULT_PER_PAGE): Promise<PaginatedResponse<HistoricSite>> {
  const base = getApiBaseUrl();
  const query = buildQuery({ page, per_page: perPage });
  const url = `${base}/me/favorites${query}`;
  const res = await fetch(url, {
    headers: { 'Accept': 'application/json' },
    credentials: 'include',
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Error al cargar favoritos (${res.status}): ${text}`);
  }
  return res.json();
}

export async function toggleFavorite(siteId: number, favorite: boolean): Promise<void> {
  const base = getApiBaseUrl();
  const method = favorite ? 'PUT' : 'DELETE';
  const url = `${base}/sites/${siteId}/favorite`;
  const res = await fetch(url, {
    method,
    headers: { 'Accept': 'application/json' },
    credentials: 'include',
  });
  if (!res.ok && res.status !== 204) {
    const text = await res.text().catch(() => '');
    throw new Error(`Error al actualizar favorito (${res.status}): ${text}`);
  }
}

export async function fetchFilterOptions(): Promise<FilterOptions> {
  const base = getApiBaseUrl();
  const url = `${base}/sites/filter-options`;
  const res = await fetch(url, {
    headers: { 'Accept': 'application/json' },
    credentials: 'omit',
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Error al cargar opciones de filtro (${res.status}): ${text}`);
  }
  return res.json();
}
