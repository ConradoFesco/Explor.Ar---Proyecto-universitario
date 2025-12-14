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
  user?: {
    id: number | null;
    name: string | null;
  };
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
    brief_description: s.short_description ?? null,
    city: s.city ?? null,
    province: s.province ?? null,
    state: s.state_of_conservation ?? null,
    tags: Array.isArray(s.tags)
      ? s.tags.map((t: any) =>
          typeof t === 'string' ? t : (t.name ?? t.slug ?? String(t))
        )
      : [],
    cover_image_url: s.cover_image_url ?? s.cover_image?.url_publica ?? null,
    rating: s.rating ?? null,
    created_at: s.inserted_at,
    latitude: s.lat ?? null,
    longitude: s.long ?? null,
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
    fav: params.favoritesOnly ? '1' : undefined,
  });
  const url = `${base}/sites${query}`;
  const res = await fetch(url, {
    headers: { 'Accept': 'application/json' },
    credentials: 'include', 
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Error al cargar sitios (${res.status}): ${text}`);
  }
  const raw = await res.json();
  const itemsSource = (raw.data ?? []) as any[];
  const items: HistoricSite[] = itemsSource.map(mapSiteFromBackend);
  const meta = raw.meta ?? {};

  const pageValue = meta.page ?? 1;
  const perPageValue = meta.per_page ?? (params.perPage ?? DEFAULT_PER_PAGE);
  const totalValue = meta.total ?? items.length;
  const totalPagesValue =
    meta.total_pages ??
    meta.pages ??
    (perPageValue > 0 ? Math.ceil(totalValue / perPageValue) : 1);

  return {
    items,
    page: pageValue,
    per_page: perPageValue,
    total: totalValue,
    total_pages: totalPagesValue,
  };
}

export async function fetchMyFavorites(page = 1, perPage = DEFAULT_PER_PAGE): Promise<PaginatedResponse<HistoricSite>> {
  const base = getApiBaseUrl();
  const safePerPage = Math.min(Math.max(perPage, 1), 100);
  const query = buildQuery({ page, per_page: safePerPage });
  const url = `${base}/me/favorites${query}`;
  const res = await fetch(url, {
    headers: { 'Accept': 'application/json' },
    credentials: 'include',
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Error al cargar favoritos (${res.status}): ${text}`);
  }
  const raw = await res.json();
  const itemsSource = (raw.data ?? []) as any[];
  const items: HistoricSite[] = itemsSource.map(mapSiteFromBackend);
  const meta = raw.meta ?? {};

  const pageValue = meta.page ?? page;
  const perPageValue = meta.per_page ?? safePerPage;
  const totalValue = meta.total ?? items.length;
  const totalPagesValue =
    perPageValue > 0 ? Math.max(1, Math.ceil(totalValue / perPageValue)) : 1;

  return {
    items,
    page: pageValue,
    per_page: perPageValue,
    total: totalValue,
    total_pages: totalPagesValue,
  };
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
    const text = await res.text().catch(() => '');
      
      if (res.status === 401) {
        throw new Error('AUTH_REQUIRED: Debe iniciar sesión para marcar como favorito');
      }
      
      throw new Error(`Error al actualizar favorito (${res.status}): ${text || 'Error desconocido'}`);
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
    const text = await res.text().catch(() => '');
    throw new Error(`Error al cargar opciones de filtro (${res.status}): ${text}`);
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
      const text = await res.text().catch(() => '');
      throw new Error(`Error al cargar sitio (${res.status}): ${text}`);
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

export async function fetchSiteReviews(siteId: number, page = 1, perPage = 25): Promise<ReviewsResponse> {
  const base = getApiBaseUrl();
  const query = buildQuery({ page, per_page: perPage });
  const url = `${base}/sites/${siteId}/reviews${query}`;
  
  const res = await fetch(url, {
    headers: { 'Accept': 'application/json' },
    credentials: 'include',
  });
  
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Error al cargar reseñas (${res.status}): ${text}`);
  }
  
  const raw = await res.json();

  const itemsSource = (raw.data ?? []) as any[];
  const meta = raw.meta ?? {};

  const mapped: Review[] = itemsSource.map((r: any) => {
    const user = r.user ?? {
      id: null,
      name: null,
    };
    const rating = Number(r.rating ?? 0);
    const content = (r.comment ?? r.content ?? '').toString();
    const createdAt = (r.inserted_at ?? r.created_at ?? null) as string | null;
    const updatedAt = (r.updated_at ?? null) as string | null;
    const authorName = (r.author_name ?? user.name ?? null) as string | null;

    return {
      id: Number(r.id),
      site_id: Number(r.site_id),
      rating,
      content,
      comment: content,
      inserted_at: createdAt,
      created_at: createdAt,
      updated_at: updatedAt,
      status: r.status,
      author_name: authorName,
      user,
    };
  });

  const approvedReviews = mapped.filter(r => !r.status || r.status === 'approved');

  return {
    reviews: approvedReviews,
    pagination: {
      page: meta.page ?? page,
      per_page: meta.per_page ?? perPage,
      total: meta.total ?? approvedReviews.length,
      pages:
        meta.pages ??
        (perPage > 0 ? Math.ceil((meta.total ?? approvedReviews.length) / perPage) : 1),
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
    const text = await res.text().catch(() => '');
    let errorMsg = text;
    try {
      const errorData = JSON.parse(text);
      errorMsg = errorData.error || text;
    } catch {
    }
    throw new Error(`Error al crear reseña (${res.status}): ${errorMsg}`);
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
    const text = await res.text().catch(() => '');
    let errorMsg = text;
    try {
      const errorData = JSON.parse(text);
      errorMsg = errorData.error || text;
    } catch {
    }
    throw new Error(`Error al actualizar reseña (${res.status}): ${errorMsg}`);
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
    const text = await res.text().catch(() => '');
    let errorMsg = text;
    try {
      const errorData = JSON.parse(text);
      errorMsg = errorData.error || text;
    } catch {
    }
    throw new Error(`Error al eliminar reseña (${res.status}): ${errorMsg}`);
  }
}

export async function getMyReview(siteId: number): Promise<Review | null> {
  const base = getApiBaseUrl();
  const url = `${base}/sites/${siteId}/reviews/me`;
  const res = await fetch(url, {
    method: 'GET',
    headers: { 
      'Accept': 'application/json',
    },
    credentials: 'include',
  });
  if (!res.ok) {
    if (res.status === 401) {
      return null;
    }
    const text = await res.text().catch(() => '');
    throw new Error(`Error al obtener reseña (${res.status}): ${text}`);
  }
  const data = await res.json();
  const raw = data.review;
  if (!raw) return null;

  const content = (raw.comment ?? '').toString();
  const createdAt = (raw.inserted_at ?? null) as string | null;
  const updatedAt = (raw.updated_at ?? null) as string | null;
  const user = raw.user ?? {
    id: null,
    name: null,
  };
  
  return {
    id: Number(raw.id),
    site_id: Number(raw.site_id),
    rating: Number(raw.rating ?? 0),
    content,
    comment: content,
    inserted_at: createdAt,
    created_at: createdAt,
    updated_at: updatedAt,
    status: raw.status,
    user,
  };
}