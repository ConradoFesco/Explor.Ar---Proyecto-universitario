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
  user: {
    id: number | null;
    mail: string | null;
    name: string | null;
  };
  rating: number;
  content: string;
  status: string;
  created_at: string | null;
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
    brief_description: s.brief_description ?? null,
    city: s.city ?? null,
    province: s.province ?? null,
    state: s.state_name ?? s.state ?? null,
    tags: Array.isArray(s.tags) 
      ? s.tags.map((t: any) => t.name ?? t.slug ?? String(t)) 
      : [],
    cover_image_url: s.cover_image_url ?? s.cover_image?.url_publica ?? null,
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
    credentials: 'include', // Incluir credenciales para que el backend pueda determinar is_favorite
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
  const raw = await res.json();
  // Mapear los items usando la misma función que fetchPublicSites
  const items: HistoricSite[] = (raw.items || []).map(mapSiteFromBackend);
  return {
    items,
    page: raw.page ?? page,
    per_page: raw.per_page ?? perPage,
    total: raw.total ?? items.length,
    total_pages: raw.total_pages ?? 1,
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
      
      // Mejorar mensaje de error según el código de estado
      if (res.status === 401) {
        throw new Error('AUTH_REQUIRED: Debe iniciar sesión para marcar como favorito');
      }
      
      throw new Error(`Error al actualizar favorito (${res.status}): ${text || 'Error desconocido'}`);
    }
  } catch (error: unknown) {
    // Si es un error de red (CORS, conexión, etc.)
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
    // Intentar primero con credenciales si se solicita (para obtener is_favorite)
    // Si falla, intentar sin credenciales
    let res = await fetch(url, {
      headers: { 'Accept': 'application/json' },
      credentials: includeAuth ? 'include' : 'omit',
    });
    
    // Si falla por autenticación y no se solicitó, intentar sin credenciales
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
    
    // Verificar que la respuesta sea JSON
    const contentType = res.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      const text = await res.text().catch(() => '');
      throw new Error(`Respuesta no es JSON. Content-Type: ${contentType}, Body: ${text.substring(0, 200)}`);
    }
    
    const raw = await res.json();
    
    // Mapear el sitio del backend
    const site: HistoricSiteDetail = {
      id: raw.id,
      name: raw.name,
      brief_description: raw.brief_description ?? null,
      complete_description: raw.complete_description ?? null,
      city: raw.city_name ?? raw.city ?? null,
      province: raw.province_name ?? raw.province ?? null,
      state: raw.state_name ?? raw.state ?? null,
      city_name: raw.city_name ?? null,
      province_name: raw.province_name ?? null,
      state_name: raw.state_name ?? null,
      category_name: raw.category_name ?? null,
      tags: Array.isArray(raw.tags) 
        ? raw.tags.map((t: any) => ({ id: t.id, name: t.name, slug: t.slug }))
        : [],
      cover_image_url: raw.cover_image?.url_publica ?? raw.cover_image_url ?? null,
      rating: raw.rating ?? null,
      created_at: raw.created_at,
      latitude: raw.latitude ? parseFloat(String(raw.latitude)) : null,
      longitude: raw.longitude ? parseFloat(String(raw.longitude)) : null,
      is_favorite: raw.is_favorite ?? false,
      images: Array.isArray(raw.images) ? raw.images : [],
      cover_image: raw.cover_image ?? null,
    };
    
    return site;
  } catch (error: any) {
    // Mejorar el mensaje de error para debugging
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`Error de red al cargar sitio: ${error.message}. Verifica que el servidor esté corriendo y la URL sea correcta.`);
    }
    throw error;
  }
}

export async function fetchSiteReviews(siteId: number, page = 1, perPage = 25): Promise<ReviewsResponse> {
  const base = getApiBaseUrl();
  const query = buildQuery({ page, per_page: perPage });
  // Usar la ruta pública que solo muestra reseñas aprobadas
  const url = `${base}/public/sites/${siteId}/reviews${query}`;
  
  const res = await fetch(url, {
    headers: { 'Accept': 'application/json' },
    credentials: 'omit', // No necesita autenticación
  });
  
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Error al cargar reseñas (${res.status}): ${text}`);
  }
  
  const raw = await res.json();
  
  // La API pública ya filtra solo reseñas aprobadas, pero por seguridad también filtramos aquí
  const approvedReviews = (raw.reviews || []).filter((r: Review) => r.status === 'approved');
  
  return {
    reviews: approvedReviews,
    pagination: raw.pagination || {
      page: page,
      per_page: perPage,
      total: approvedReviews.length,
      pages: Math.ceil(approvedReviews.length / perPage),
    },
  };
}

export async function createReview(siteId: number, rating: number, content: string): Promise<Review> {
  const base = getApiBaseUrl();
  const url = `${base}/sites/${siteId}/reviews`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ rating, content }),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    let errorMsg = text;
    try {
      const errorData = JSON.parse(text);
      errorMsg = errorData.error || text;
    } catch {
      // Si no es JSON, usar el texto tal cual
    }
    throw new Error(`Error al crear reseña (${res.status}): ${errorMsg}`);
  }
  return res.json();
}

export async function updateReview(siteId: number, reviewId: number, rating: number, content: string): Promise<Review> {
  const base = getApiBaseUrl();
  const url = `${base}/sites/${siteId}/reviews/${reviewId}`;
  const res = await fetch(url, {
    method: 'PUT',
    headers: { 
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ rating, content }),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    let errorMsg = text;
    try {
      const errorData = JSON.parse(text);
      errorMsg = errorData.error || text;
    } catch {
      // Si no es JSON, usar el texto tal cual
    }
    throw new Error(`Error al actualizar reseña (${res.status}): ${errorMsg}`);
  }
  return res.json();
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
      // Si no es JSON, usar el texto tal cual
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
      return null; // No autenticado
    }
    const text = await res.text().catch(() => '');
    throw new Error(`Error al obtener reseña (${res.status}): ${text}`);
  }
  const data = await res.json();
  return data.review || null;
}