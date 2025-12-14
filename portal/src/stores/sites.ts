import { defineStore } from 'pinia'
import type { HistoricSite, PaginatedResponse, SiteSearchParams } from '@/lib/api'
import { fetchPublicSites } from '@/lib/api'

export type SortOption = {
  field: 'created_at' | 'name' | 'rating'
  dir: 'asc' | 'desc'
}

export type SitesState = {
  items: HistoricSite[]
  page: number | string | undefined
  perPage: number | string | undefined
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
  lat: number | string | null | undefined
  long: number | string | null | undefined
  radius: number | string | null | undefined
  sort: SortOption | string | undefined
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
    const matchesText = !text ||
      s.name?.toLowerCase().includes(textLower) ||
      (s.brief_description || '').toLowerCase().includes(textLower)
    
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
    page: undefined,
    perPage: undefined,
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
    lat: undefined,
    long: undefined,
    radius: undefined,
    sort: undefined,
  }),
  getters: {
    hasMore(state): boolean {
      if (state.page === undefined || state.page === null) return false
      const pageNum = typeof state.page === 'number' ? state.page : Number(state.page)
      if (!Number.isFinite(pageNum)) return false
      return (pageNum as number) < state.totalPages
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
      if (typeof state.sort === 'string') {
        qp.sort = state.sort
      } else if (state.sort) {
        qp.sort = `${state.sort.field}:${state.sort.dir}`
      }
      if (state.page !== undefined && state.page !== null) {
        qp.page = String(state.page)
      }
      if (state.perPage !== undefined && state.perPage !== null) {
        qp.perPage = String(state.perPage)
      }
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
      this.lat = query.lat as string | number | null | undefined
      this.long = query.long as string | number | null | undefined
      this.radius = query.radius as string | number | null | undefined
      this.sort = query.sort as string | undefined
      this.page = query.page as string | number | undefined
      this.perPage = query.perPage as string | number | undefined
    },
    toSearchParams(): SiteSearchParams {
      let orderBy: 'created_at' | 'name' | 'rating' | undefined = undefined
      let orderDir: 'asc' | 'desc' | undefined = undefined
      
      if (typeof this.sort === 'string') {
        const parts = this.sort.split(':')
        if (parts.length >= 2 && parts[0] && parts[1]) {
          orderBy = parts[0] as any
          orderDir = parts[1] as any
        } else if (parts.length === 1 && parts[0]) {
          orderBy = parts[0] as any
          orderDir = undefined
        }
      } else if (this.sort) {
        orderBy = this.sort.field
        orderDir = this.sort.dir
      }
      
      return {
        text: this.text || undefined,
        city: this.city || null,
        province: this.province || null,
        tags: this.tags.length ? this.tags : null,
        orderBy,
        orderDir,
        lat: this.lat as any,
        long: this.long as any,
        radius: this.radius as any,
        page: this.page as any,
        perPage: this.perPage as any,
        favoritesOnly: this.favoritesOnly,
      }
    },
    resetFilters() {
      this.text = ''
      this.city = ''
      this.province = ''
      this.tags = []
      this.favoritesOnly = false
      this.lat = undefined
      this.long = undefined
      this.radius = undefined
      this.sort = undefined
      this.page = undefined
      this.perPage = undefined
    },
    async loadFirstPage() {
      this.page = undefined
      await this.loadPage(true)
    },
    async loadNextPage() {
      if (!this.hasMore || this.isLoading || this.isNextLoading) return
      const currentPage = typeof this.page === 'number' ? this.page : (typeof this.page === 'string' ? Number(this.page) : 1)
      this.page = currentPage + 1
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
        let response: PaginatedResponse<HistoricSite> = await fetchPublicSites(params)

        const pageItems = response.items

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
