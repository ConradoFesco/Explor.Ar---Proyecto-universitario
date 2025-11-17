import { defineStore } from 'pinia'
import type { HistoricSite, PaginatedResponse, SiteSearchParams } from '@/lib/api'
import { fetchPublicSites, fetchMyFavorites, toggleFavorite } from '@/lib/api'

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

function filterFavorites(items: HistoricSite[], text: string, city: string, province: string, tags: string[]): HistoricSite[] {
  const textLower = text.toLowerCase()
  return items.filter((s) => {
    const matchesText = !text ||
      s.name?.toLowerCase().startsWith(textLower) ||
      (s.brief_description || '').toLowerCase().startsWith(textLower)
    const matchesCity = !city || (s.city || '').toLowerCase() === city.toLowerCase()
    const matchesProvince = !province || (s.province || '').toLowerCase() === province.toLowerCase()
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
        
        if (params.favoritesOnly) {
          response = await fetchMyFavorites(params.page ?? 1, params.perPage ?? 20)
          let filtered = filterFavorites(response.items, this.text, this.city, this.province, this.tags)
          
          if (this.sort.field === 'name') {
            filtered = sortByName(filtered, this.sort.dir)
          }
          
          response.items = filtered
          response.total = filtered.length
          response.total_pages = Math.max(1, Math.ceil(filtered.length / (params.perPage ?? 20)))
        } else {
          response = await fetchPublicSites(params)
        }
        
        let pageItems = response.items
        if (!params.favoritesOnly && this.sort.field === 'name') {
          pageItems = sortByName(pageItems, this.sort.dir)
        }
        
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
    async setFavorite(siteId: number, makeFav: boolean) {
      const idx = this.items.findIndex(s => s.id === siteId)
      const currentItem = idx >= 0 ? this.items[idx] : null
      const previousState = currentItem?.is_favorite ?? false
      
      // Optimistic update
      if (currentItem) {
        this.items[idx] = { ...currentItem, is_favorite: makeFav } as HistoricSite
      }
      
      try {
        await toggleFavorite(siteId, makeFav)
      } catch (error) {
        // Revertir cambio optimista si falla
        if (currentItem) {
          this.items[idx] = { ...currentItem, is_favorite: previousState } as HistoricSite
        }
        throw error // Re-lanzar para que el componente maneje el error
      }
    },
  },
})
