import { defineStore } from 'pinia'
import type { HistoricSite, PaginatedResponse, SiteSearchParams } from '@/lib/api'
import { fetchPublicSites, fetchMyFavorites } from '@/lib/api'

export type SortOption = {
  field: 'created_at' | 'name' | 'rating'
  dir: 'asc' | 'desc'
}

export type SitesState = {
  items: HistoricSite[]
  page: number
  perPage: number
  total: number
  totalPages: number
  isLoading: boolean
  isNextLoading: boolean
  error: string | null
  text: string
  city: string
  province: string
  tags: string[]
  favoritesOnly: boolean
  lat: number | null
  long: number | null
  radius: number | null
  sort: SortOption
}

function parseNumber(value: unknown): number | null {
  const n = typeof value === 'string' ? Number(value) : (value as number)
  return Number.isFinite(n) ? (n as number) : null
}

function parseSort(sortRaw: string): SortOption {
  const [field, dir] = sortRaw.split(':')
  if ((field === 'created_at' || field === 'name' || field === 'rating') && (dir === 'asc' || dir === 'desc')) {
    return { field, dir } as SortOption
  }
  return { field: 'created_at', dir: 'desc' }
}

function sortByName(items: HistoricSite[], dir: 'asc' | 'desc'): HistoricSite[] {
  return [...items].sort((a, b) => {
    const an = (a.name || '').toLowerCase()
    const bn = (b.name || '').toLowerCase()
    return dir === 'asc' ? an.localeCompare(bn) : bn.localeCompare(an)
  })
}

function sortByRating(items: HistoricSite[], dir: 'asc' | 'desc'): HistoricSite[] {
  // El backend ya calcula y devuelve el rating, solo necesitamos ordenar
  return [...items].sort((a, b) => {
    const aRating = a.rating ?? 0
    const bRating = b.rating ?? 0
    
    if (dir === 'asc') {
      return aRating - bRating
    } else {
      return bRating - aRating
    }
  })
}

function filterSites(
  items: HistoricSite[],
  text: string,
  city: string,
  province: string,
  tags: string[]
): HistoricSite[] {
  const textLower = text.toLowerCase()
  return items.filter((s) => {
    // Filtrar por texto (nombre o descripción)
    const matchesText = !text ||
      s.name?.toLowerCase().includes(textLower) ||
      (s.brief_description || '').toLowerCase().includes(textLower)
    
    // Filtrar por ciudad
    const matchesCity = !city || (s.city || '').toLowerCase() === city.toLowerCase()
    
    // Filtrar por provincia
    const matchesProvince = !province || (s.province || '').toLowerCase() === province.toLowerCase()
    
    // Filtrar por tags
    const matchesTags = !tags.length || tags.every(t => 
      s.tags?.map(x => x.toLowerCase()).includes(t.toLowerCase())
    )
    
    return matchesText && matchesCity && matchesProvince && matchesTags
  })
}


export const useSitesStore = defineStore('sites', {
  state: (): SitesState => ({
    items: [],
    page: 1,
    perPage: 20,
    total: 0,
    totalPages: 0,
    isLoading: false,
    isNextLoading: false,
    error: null,
    text: '',
    city: '',
    province: '',
    tags: [],
    favoritesOnly: false,
    lat: null,
    long: null,
    radius: null,
    sort: { field: 'created_at', dir: 'desc' },
  }),
  getters: {
    hasMore(state): boolean {
      return state.page < state.totalPages
    },
    queryParams(state): Record<string, string> {
      const qp: Record<string, string> = {}
      if (state.text) qp.q = state.text
      if (state.city) qp.city = state.city
      if (state.province) qp.province = state.province
      if (state.tags.length) qp.tags = state.tags.join(',')
      if (state.favoritesOnly) qp.fav = '1'
      if (state.lat != null && state.long != null) {
        qp.lat = String(state.lat)
        qp.long = String(state.long)
      }
      if (state.radius != null) qp.radius = String(state.radius)
      qp.sort = `${state.sort.field}:${state.sort.dir}`
      qp.page = String(state.page)
      qp.perPage = String(state.perPage)
      return qp
    },
  },
  actions: {
    fromRouteQuery(query: Record<string, string | string[] | null | undefined>) {
      this.text = (query.q as string) || ''
      this.city = (query.city as string) || ''
      this.province = (query.province as string) || ''
      const rawTags = (query.tags as string) || ''
      this.tags = rawTags ? rawTags.split(',').map(t => t.trim()).filter(Boolean) : []
      this.favoritesOnly = (query.fav as string) === '1'
      this.lat = parseNumber(query.lat)
      this.long = parseNumber(query.long)
      this.radius = parseNumber(query.radius)
      this.sort = parseSort((query.sort as string) || 'created_at:desc')
      this.page = parseNumber(query.page) ?? 1
      this.perPage = parseNumber(query.perPage) ?? 20
    },
    toSearchParams(): SiteSearchParams {
      return {
        text: this.text || undefined,
        city: this.city || null,
        province: this.province || null,
        tags: this.tags.length ? this.tags : null,
        orderBy: this.sort.field,
        orderDir: this.sort.dir,
        lat: this.lat,
        long: this.long,
        radius: this.radius,
        page: this.page,
        perPage: this.perPage,
        favoritesOnly: this.favoritesOnly,
      }
    },
    resetFilters() {
      this.text = ''
      this.city = ''
      this.province = ''
      this.tags = []
      this.favoritesOnly = false
      this.lat = null
      this.long = null
      this.radius = null
      this.sort = { field: 'created_at', dir: 'desc' }
      this.page = 1
    },
    async loadFirstPage() {
      this.page = 1
      await this.loadPage(true)
    },
    async loadNextPage() {
      if (!this.hasMore || this.isLoading || this.isNextLoading) return
      this.page += 1
      await this.loadPage(false)
    },
    async loadPage(replace: boolean) {
      if (replace) {
        this.isLoading = true
        this.error = null
      } else {
        this.isNextLoading = true
      }
      try {
        const params = this.toSearchParams()
        let response: PaginatedResponse<HistoricSite>
        
        if (this.favoritesOnly) {
          try {
            // Obtener todos los favoritos del usuario
            let allFavoritesItems: HistoricSite[] = []
            const perPage = 100
            let totalPages = 1
            
            const firstPage = await fetchMyFavorites(1, perPage)
            allFavoritesItems = [...firstPage.items]
            totalPages = firstPage.total_pages
            
            if (totalPages > 1) {
              const remainingPages = []
              for (let page = 2; page <= totalPages; page++) {
                remainingPages.push(fetchMyFavorites(page, perPage))
              }
              const remainingResults = await Promise.all(remainingPages)
              for (const result of remainingResults) {
                allFavoritesItems = [...allFavoritesItems, ...result.items]
              }
            }
            
            // Aplicar filtros adicionales (texto, ciudad, provincia, tags)
            let filtered = filterSites(
              allFavoritesItems,
              this.text,
              this.city,
              this.province,
              this.tags
            )
            
            // Aplicar ordenamiento si es necesario
            // Para favoritos, obtenemos todos y luego filtramos/ordenamos en el frontend
            if (this.sort.field === 'name') {
              filtered = sortByName(filtered, this.sort.dir)
            } else if (this.sort.field === 'rating') {
              // Ordenar por rating (el backend ya lo calcula, solo ordenamos aquí)
              filtered = sortByRating(filtered, this.sort.dir)
            }
            
            // Aplicar paginación
            const resultPerPage = params.perPage ?? 20
            const resultCurrentPage = params.page ?? 1
            const startIndex = (resultCurrentPage - 1) * resultPerPage
            const endIndex = startIndex + resultPerPage
            const paginatedItems = filtered.slice(startIndex, endIndex)
            
            response = {
              items: paginatedItems,
              total: filtered.length,
              total_pages: Math.max(1, Math.ceil(filtered.length / resultPerPage)),
              page: resultCurrentPage,
              per_page: resultPerPage
            }
          } catch (authError: any) {
            if (authError?.message?.includes('401') || authError?.message?.includes('autenticado')) {
              this.favoritesOnly = false
              response = await fetchPublicSites({ ...params, favoritesOnly: false })
            } else {
              throw authError
            }
          }
        } else {
          response = await fetchPublicSites(params)
          
          // El ordenamiento por rating ahora se hace en el backend
          // Solo ordenamos por nombre en el frontend si es necesario
          if (this.sort.field === 'name') {
            response.items = sortByName(response.items, this.sort.dir)
          }
        }
        
        let pageItems = response.items
        
        if (replace) {
          this.items = pageItems
        } else {
          this.items = [...this.items, ...pageItems]
        }
        this.total = response.total
        this.totalPages = response.total_pages
      } catch (e: any) {
        this.error = e?.message || 'Error al cargar sitios'
      } finally {
        this.isLoading = false
        this.isNextLoading = false
      }
    },
  },
})
