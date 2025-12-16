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

export type SiteImage = {
  id: number;
  id_site: number;
  url_publica: string;
  titulo_alt: string;
  descripcion?: string | null;
  orden: number;
  es_portada: boolean;
};

export type HistoricSiteDetail = HistoricSite & {
  complete_description?: string | null;
  city_name?: string | null;
  province_name?: string | null;
  state_name?: string | null;
  category_name?: string | null;
  images?: SiteImage[];
  cover_image?: SiteImage | null;
  tags?: Array<{ id: number; name: string; slug: string }>;
};

export type Review = {
  id: number;
  site_id: number;
  rating: number;
  content: string;
  comment?: string; 
  inserted_at?: string | null;
  created_at: string | null;
  updated_at?: string | null;
  status?: string;
  author_name?: string | null; 
  user_id?: number | null;
};

export type ReviewsResponse = {
  reviews: Review[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
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

export function getApiBaseUrl(): string {
  const envUrl = (import.meta.env.VITE_API_BASE_URL as string || 'https://admin-grupo06.proyecto2025.linti.unlp.edu.ar/api');
  return envUrl ?? '/api';
}

async function handleHttpError(res: Response, defaultMessage: string): Promise<never> {
  const text = await res.text().catch(() => '');
  let errorMessage = text;
  
  try {
    const errorData = JSON.parse(text);
    if (errorData && typeof errorData === 'object') {
      errorMessage = errorData.error?.message || errorData.error || text;
    }
  } catch {
  }
  
  throw new Error(`${defaultMessage} (${res.status}): ${errorMessage || 'Error desconocido'}`);
}


function parsePaginatedResponse<T>(
  raw: any,
  mapper: (item: any) => T,
  defaultPage?: number,
  defaultPerPage?: number
): PaginatedResponse<T> {
  const itemsSource = (raw.data ?? []) as any[];
  const items: T[] = itemsSource.map(mapper);
  const meta = raw.meta ?? {};

  const pageValue = (typeof meta.page === 'number' ? meta.page : defaultPage) ?? 1;
  const perPageValue = (typeof meta.per_page === 'number' ? meta.per_page : defaultPerPage) ?? DEFAULT_PER_PAGE;
  const totalValue = (typeof meta.total === 'number' ? meta.total : items.length);
  const totalPagesValue =
    (typeof meta.total_pages === 'number' ? meta.total_pages : undefined) ??
    (typeof meta.pages === 'number' ? meta.pages : undefined) ??
    (perPageValue > 0 ? Math.ceil(totalValue / perPageValue) : 1);

  return {
    items,
    page: pageValue,
    per_page: perPageValue,
    total: totalValue,
    total_pages: totalPagesValue,
  };
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

function mapSiteFromBackend(s: Record<string, unknown>): HistoricSite {
  const mapTag = (tag: unknown): string => {
    if (typeof tag === 'string') return tag;
    if (tag && typeof tag === 'object') {
      const tagObj = tag as { name?: unknown; slug?: unknown };
      return String(tagObj.name ?? tagObj.slug ?? tag);
    }
    return String(tag ?? '');
  };

  return {
    id: Number(s.id) || 0,
    name: String(s.name || ''),
    brief_description: s.short_description ? String(s.short_description) : null,
    city: s.city ? String(s.city) : null,
    province: s.province ? String(s.province) : null,
    state: s.state_of_conservation ? String(s.state_of_conservation) : null,
    tags: Array.isArray(s.tags) ? s.tags.map(mapTag) : [],
    cover_image_url: s.cover_image_url 
      ? String(s.cover_image_url) 
      : (s.cover_image && typeof s.cover_image === 'object' && 'url_publica' in s.cover_image)
        ? String((s.cover_image as { url_publica: unknown }).url_publica)
        : null,
    rating: s.rating != null ? Number(s.rating) : null,
    created_at: s.inserted_at ? String(s.inserted_at) : undefined,
    latitude: s.lat != null ? Number(s.lat) : null,
    longitude: s.long != null ? Number(s.long) : null,
    is_favorite: Boolean(s.is_favorite ?? false),
  };
}

function mapOrderBy(orderBy?: SiteSearchParams['orderBy'], dir?: SiteSearchParams['orderDir']): string | undefined {
  if (!orderBy || !dir) {
    return undefined;
  }
  
  if (dir !== 'asc' && dir !== 'desc') {
    return `${String(orderBy)}-${String(dir)}`;
  }
  
  if (orderBy === 'created_at') {
    return dir === 'asc' ? 'oldest' : 'latest';
  }
  
  if (orderBy === 'rating') {
    return dir === 'asc' ? 'rating-1-5' : 'rating-5-1';
  }
  
  if (orderBy === 'name') {
    return dir === 'asc' ? 'name-asc' : 'name-desc';
  }
  
  return `${String(orderBy)}-${String(dir)}`;
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
    radius: params.radius,
    page: params.page,
    per_page: params.perPage,
    fav: params.favoritesOnly ? '1' : undefined,
  });
  const url = `${base}/sites${query}`;
  const res = await fetch(url, {
    headers: { 'Accept': 'application/json' },
    credentials: 'include', 
  });
  if (!res.ok) {
    await handleHttpError(res, 'Error al cargar sitios');
  }
  const raw = await res.json();
  return parsePaginatedResponse(raw, mapSiteFromBackend, 1, params.perPage ?? DEFAULT_PER_PAGE);
}

export async function fetchMyFavorites(page?: number, perPage?: number): Promise<PaginatedResponse<HistoricSite>> {
  const base = getApiBaseUrl();
  const query = buildQuery({ page, per_page: perPage });
  const url = `${base}/me/favorites${query}`;
  const res = await fetch(url, {
    headers: { 'Accept': 'application/json' },
    credentials: 'include',
  });
  if (!res.ok) {
    await handleHttpError(res, 'Error al cargar favoritos');
  }
  const raw = await res.json();
  return parsePaginatedResponse(raw, mapSiteFromBackend, page, perPage);
}

export async function toggleFavorite(siteId: number, favorite: boolean): Promise<void> {
  const base = getApiBaseUrl();
  const method = favorite ? 'PUT' : 'DELETE';
  const url = `${base}/sites/${siteId}/favorite`;
  
  try {
    const res = await fetch(url, {
      method,
      headers: { 'Accept': 'application/json' },
      credentials: 'include',
    });
    
    if (!res.ok && res.status !== 204) {
      if (res.status === 401) {
        throw new Error('AUTH_REQUIRED: Debe iniciar sesión para marcar como favorito');
      }
      await handleHttpError(res, 'Error al actualizar favorito');
    }
  } catch (error: unknown) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('NETWORK_ERROR: Error de conexión. Verifica tu conexión a internet.');
    }
    throw error;
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
    await handleHttpError(res, 'Error al cargar opciones de filtro');
  }
  return res.json();
}

export async function fetchSiteDetail(siteId: number, includeAuth = false): Promise<HistoricSiteDetail> {
  const base = getApiBaseUrl();
  const url = `${base}/sites/${siteId}`;
  
  try {
    let res = await fetch(url, {
      headers: { 'Accept': 'application/json' },
      credentials: includeAuth ? 'include' : 'omit',
    });
    
    if (!res.ok && res.status === 401 && includeAuth) {
      res = await fetch(url, {
        headers: { 'Accept': 'application/json' },
        credentials: 'omit',
      });
    }
    
    if (!res.ok) {
      await handleHttpError(res, 'Error al cargar sitio');
    }
    
    const contentType = res.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      const text = await res.text().catch(() => '');
      throw new Error(`Respuesta no es JSON. Content-Type: ${contentType}, Body: ${text.substring(0, 200)}`);
    }
    
    const raw = await res.json();
    
    const site: HistoricSiteDetail = {
      id: raw.id,
      name: raw.name,
      brief_description: raw.short_description ?? null,
      complete_description: raw.description ?? null,
      city: raw.city ?? null,
      province: raw.province ?? null,
      state: raw.state_of_conservation ?? null,
      city_name: raw.city ?? null,
      province_name: raw.province ?? null,
      state_name: raw.state_of_conservation ?? null,
      category_name: raw.category_name ?? null,
      tags: Array.isArray(raw.tags) 
        ? raw.tags.map((t: any) => ({ id: t.id, name: t.name, slug: t.slug }))
        : [],
      cover_image_url: raw.cover_image?.url_publica ?? raw.cover_image_url ?? null,
      rating: raw.rating ?? null,
      created_at: raw.inserted_at ?? raw.created_at ?? null,
      latitude: raw.lat != null
        ? parseFloat(String(raw.lat))
        : (raw.latitude != null ? parseFloat(String(raw.latitude)) : null),
      longitude: raw.long != null
        ? parseFloat(String(raw.long))
        : (raw.longitude != null ? parseFloat(String(raw.longitude)) : null),
      is_favorite: raw.is_favorite ?? false,
      images: Array.isArray(raw.images) ? raw.images : [],
      cover_image: raw.cover_image ?? null,
    };
    
    return site;
  } catch (error: any) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`Error de red al cargar sitio: ${error.message}. Verifica que el servidor esté corriendo y la URL sea correcta.`);
    }
    throw error;
  }
}

export async function fetchSiteReviews(siteId: number, page?: number, perPage?: number): Promise<ReviewsResponse> {
  const base = getApiBaseUrl();
  const query = buildQuery({ page, per_page: perPage });
  const url = `${base}/sites/${siteId}/reviews${query}`;
  
  const res = await fetch(url, {
    headers: { 'Accept': 'application/json' },
    credentials: 'include',
  });
  
  if (!res.ok) {
    await handleHttpError(res, 'Error al cargar reseñas');
  }
  
  const raw = await res.json();

  const itemsSource = (raw.data ?? []) as any[];
  const meta = raw.meta ?? {};

  const mapReview = (r: Record<string, unknown>): Review => {
    const id = Number(r.id) || 0;
    const siteId = Number(r.site_id) || 0;
    const rating = r.rating != null ? Number(r.rating) : 0;
    const content = String(r.comment ?? r.content ?? '');
    const createdAt = r.inserted_at ? String(r.inserted_at) : (r.created_at ? String(r.created_at) : null);
    const updatedAt = r.updated_at ? String(r.updated_at) : null;
    const authorName = r.author_name ? String(r.author_name) : null;
    const userId = r.user_id != null ? Number(r.user_id) : null;
    const status = r.status ? String(r.status) : undefined;

    return {
      id,
      site_id: siteId,
      rating,
      content,
      comment: content,
      inserted_at: createdAt,
      created_at: createdAt,
      updated_at: updatedAt,
      status,
      author_name: authorName,
      user_id: userId,
    };
  };

  const mapped: Review[] = itemsSource.map(mapReview);

  const pageValue = meta.page ?? page ?? 1;
  const perPageValue = meta.per_page ?? perPage ?? 25;
  const totalValue = meta.total ?? mapped.length;
  const totalPagesValue =
    meta.pages ??
    (perPageValue > 0 ? Math.ceil((meta.total ?? mapped.length) / perPageValue) : 1);

  return {
    reviews: mapped,
    pagination: {
      page: pageValue as number,
      per_page: perPageValue as number,
      total: totalValue as number,
      pages: totalPagesValue as number,
    },
  };
}

export async function createReview(siteId: number, rating: number, content: string): Promise<void> {
  const base = getApiBaseUrl();
  const url = `${base}/sites/${siteId}/reviews`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ rating, comment: content }),
  });
  if (!res.ok) {
    await handleHttpError(res, 'Error al crear reseña');
  }
}

export async function updateReview(siteId: number, reviewId: number, rating: number, content: string): Promise<void> {
  const base = getApiBaseUrl();
  const url = `${base}/sites/${siteId}/reviews/${reviewId}`;
  const res = await fetch(url, {
    method: 'PUT',
    headers: { 
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ rating, comment: content }),
  });
  if (!res.ok) {
    await handleHttpError(res, 'Error al actualizar reseña');
  }
}

export async function deleteReview(siteId: number, reviewId: number): Promise<void> {
  const base = getApiBaseUrl();
  const url = `${base}/sites/${siteId}/reviews/${reviewId}`;
  const res = await fetch(url, {
    method: 'DELETE',
    headers: { 
      'Accept': 'application/json',
    },
    credentials: 'include',
  });
  if (!res.ok) {
    await handleHttpError(res, 'Error al eliminar reseña');
  }
}
