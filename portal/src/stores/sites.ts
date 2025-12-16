import { defineStore } from 'pinia'
import type { HistoricSite, PaginatedResponse, SiteSearchParams } from '@/lib/api'
import { fetchPublicSites } from '@/lib/api'

export type SortOption = {
  field: 'created_at' | 'name' | 'rating'
  dir: 'asc' | 'desc'
}

export type ValidationErrors = {
  lat?: string
  long?: string
  radius?: string
  page?: string
  perPage?: string
  sort?: string
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
  validationErrors: ValidationErrors
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

function validateAndCleanNumber(
  value: unknown,
  fieldName: string,
  min?: number,
  max?: number
): { value: number | undefined; error?: string } {
  if (value === undefined || value === null || value === '') {
    return { value: undefined }
  }

  const num = typeof value === 'string' ? Number(value) : Number(value)
  
  if (!Number.isFinite(num)) {
    return { value: undefined, error: `${fieldName} debe ser un número válido` }
  }

  if (min !== undefined && num < min) {
    return { value: undefined, error: `${fieldName} debe ser mayor o igual a ${min}` }
  }

  if (max !== undefined && num > max) {
    return { value: undefined, error: `${fieldName} debe ser menor o igual a ${max}` }
  }

  return { value: num }
}

function validateAndCleanSort(
  sortValue: string | SortOption | undefined
): { value: SortOption | string | undefined; error?: string } {
  if (!sortValue) {
    return { value: undefined }
  }

  if (typeof sortValue === 'string') {
    const parts = sortValue.split(':')
    if (parts.length === 2 && parts[0] && parts[1]) {
      const field = parts[0].trim()
      const dir = parts[1].trim().toLowerCase()
      
      const validFields = ['created_at', 'name', 'rating']
      const validDirs = ['asc', 'desc']
      
      if (!validFields.includes(field)) {
        return { value: sortValue, error: `Campo de ordenamiento inválido. Valores permitidos: ${validFields.join(', ')}` }
      }
      
      if (!validDirs.includes(dir)) {
        return { value: sortValue, error: `Dirección de ordenamiento inválida. Valores permitidos: ${validDirs.join(', ')}` }
      }
      
      return { value: sortValue }
    } else if (parts.length === 1 && parts[0]) {
      return { value: sortValue, error: 'Falta la dirección de ordenamiento (asc o desc)' }
    }
  } else if (sortValue.field && sortValue.dir) {
    const validFields = ['created_at', 'name', 'rating']
    const validDirs = ['asc', 'desc']
    
    if (!validFields.includes(sortValue.field)) {
      return { value: sortValue, error: `Campo de ordenamiento inválido. Valores permitidos: ${validFields.join(', ')}` }
    }
    
    if (!validDirs.includes(sortValue.dir)) {
      return { value: sortValue, error: `Dirección de ordenamiento inválida. Valores permitidos: ${validDirs.join(', ')}` }
    }
    
    return { value: sortValue }
  }

  return { value: sortValue }
}

function cleanString(value: unknown): string {
  if (value === undefined || value === null) return ''
  return String(value).trim()
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
    validationErrors: {},
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
    clearValidationErrors() {
      this.validationErrors = {}
    },
    setValidationError(field: keyof ValidationErrors, error: string) {
      this.validationErrors[field] = error
    },
    validateLat(value: unknown): { valid: boolean; error?: string; cleaned?: number } {
      const result = validateAndCleanNumber(value, 'Latitud', -90, 90)
      if (result.error) {
        this.setValidationError('lat', result.error)
        return { valid: false, error: result.error }
      }
      if (result.value !== undefined) {
        this.lat = result.value
        delete this.validationErrors.lat
        return { valid: true, cleaned: result.value }
      }
      this.lat = undefined
      delete this.validationErrors.lat
      return { valid: true }
    },
    validateLong(value: unknown): { valid: boolean; error?: string; cleaned?: number } {
      const result = validateAndCleanNumber(value, 'Longitud', -180, 180)
      if (result.error) {
        this.setValidationError('long', result.error)
        return { valid: false, error: result.error }
      }
      if (result.value !== undefined) {
        this.long = result.value
        delete this.validationErrors.long
        return { valid: true, cleaned: result.value }
      }
      this.long = undefined
      delete this.validationErrors.long
      return { valid: true }
    },
    validateRadius(value: unknown): { valid: boolean; error?: string; cleaned?: number } {
      const result = validateAndCleanNumber(value, 'Radio', 100, 50000)
      if (result.error) {
        this.setValidationError('radius', result.error)
        return { valid: false, error: result.error }
      }
      if (result.value !== undefined) {
        this.radius = result.value
        delete this.validationErrors.radius
        return { valid: true, cleaned: result.value }
      }
      this.radius = undefined
      delete this.validationErrors.radius
      return { valid: true }
    },
    fromRouteQuery(query: Record<string, string | string[] | null | undefined>) {
      this.clearValidationErrors()
      this.text = cleanString(query.q)
      this.city = cleanString(query.city)
      this.province = cleanString(query.province)
      const rawTags = cleanString(query.tags)
      this.tags = rawTags ? rawTags.split(',').map(t => t.trim()).filter(Boolean) : []
      this.favoritesOnly = (query.fav as string) === '1'
      
      const latResult = validateAndCleanNumber(query.lat, 'Latitud', -90, 90)
      this.lat = latResult.value
      if (latResult.error && query.lat !== undefined && query.lat !== null && query.lat !== '') {
        this.setValidationError('lat', latResult.error)
      }
      
      const longResult = validateAndCleanNumber(query.long, 'Longitud', -180, 180)
      this.long = longResult.value
      if (longResult.error && query.long !== undefined && query.long !== null && query.long !== '') {
        this.setValidationError('long', longResult.error)
      }
      
      const radiusResult = validateAndCleanNumber(query.radius, 'Radio', 100, 50000)
      this.radius = radiusResult.value
      if (radiusResult.error && query.radius !== undefined && query.radius !== null && query.radius !== '') {
        this.setValidationError('radius', radiusResult.error)
      }
      
      const pageResult = validateAndCleanNumber(query.page, 'Página', 1)
      this.page = pageResult.value
      if (pageResult.error && query.page !== undefined && query.page !== null && query.page !== '') {
        this.setValidationError('page', pageResult.error)
      }
      
      const perPageResult = validateAndCleanNumber(query.perPage, 'Elementos por página', 1, 100)
      this.perPage = perPageResult.value
      if (perPageResult.error && query.perPage !== undefined && query.perPage !== null && query.perPage !== '') {
        this.setValidationError('perPage', perPageResult.error)
      }
      
      const sortResult = validateAndCleanSort(query.sort as string | undefined)
      this.sort = sortResult.value
      if (sortResult.error && query.sort !== undefined && query.sort !== null && query.sort !== '') {
        this.setValidationError('sort', sortResult.error)
      }
    },
    toSearchParams(): SiteSearchParams {
      let orderBy: 'created_at' | 'name' | 'rating' | undefined = undefined
      let orderDir: 'asc' | 'desc' | undefined = undefined
      
      if (typeof this.sort === 'string') {
        const parts = this.sort.split(':')
        if (parts.length >= 2 && parts[0] && parts[1]) {
          const field = parts[0].trim()
          const dir = parts[1].trim().toLowerCase()
          if (['created_at', 'name', 'rating'].includes(field) && ['asc', 'desc'].includes(dir)) {
            orderBy = field as 'created_at' | 'name' | 'rating'
            orderDir = dir as 'asc' | 'desc'
          }
        } else if (parts.length === 1 && parts[0]) {
          const field = parts[0].trim()
          if (['created_at', 'name', 'rating'].includes(field)) {
            orderBy = field as 'created_at' | 'name' | 'rating'
          }
        }
      } else if (this.sort) {
        orderBy = this.sort.field
        orderDir = this.sort.dir
      }
      
      const convertToNumber = (value: number | string | null | undefined): number | undefined => {
        if (value === undefined || value === null || value === '') return undefined
        const num = typeof value === 'number' ? value : Number(value)
        return isNaN(num) ? undefined : num
      }
      
      const convertToNumberOrNull = (value: number | string | null | undefined): number | null | undefined => {
        if (value === undefined || value === null || value === '') return null
        const num = typeof value === 'number' ? value : Number(value)
        return isNaN(num) ? null : num
      }
      
      return {
        text: this.text || undefined,
        city: this.city || null,
        province: this.province || null,
        tags: this.tags.length ? this.tags : null,
        orderBy,
        orderDir,
        lat: convertToNumberOrNull(this.lat),
        long: convertToNumberOrNull(this.long),
        radius: convertToNumberOrNull(this.radius),
        page: convertToNumber(this.page),
        perPage: convertToNumber(this.perPage),
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
      this.clearValidationErrors()
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
      if (Object.keys(this.validationErrors).length > 0) {
        if (replace) {
          this.isLoading = false
        } else {
          this.isNextLoading = false
        }
        return
      }
      
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
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : 'Error al cargar sitios'
        this.error = errorMessage
        
        try {
          if (errorMessage.includes('validation') || errorMessage.includes('inválido') || errorMessage.includes('Invalid')) {
            const errorData = (error as { response?: unknown; data?: unknown })?.response || (error as { data?: unknown })?.data
            if (errorData && typeof errorData === 'object' && 'error' in errorData) {
              const errorObj = errorData.error as { details?: Record<string, unknown> }
              if (errorObj?.details) {
                const details = errorObj.details
                
                const extractError = (value: unknown): string | undefined => {
                  if (Array.isArray(value) && value.length > 0) {
                    return String(value[0])
                  }
                  if (typeof value === 'string') {
                    return value
                  }
                  return undefined
                }
                
                const orderByError = extractError(details.order_by)
                if (orderByError) {
                  this.setValidationError('sort', orderByError)
                }
                
                const radiusError = extractError(details.radius)
                if (radiusError) {
                  this.setValidationError('radius', radiusError)
                }
                
                const latError = extractError(details.lat)
                if (latError) {
                  this.setValidationError('lat', latError)
                }
                
                const longError = extractError(details.long || details.longitude)
                if (longError) {
                  this.setValidationError('long', longError)
                }
              }
            }
          }
        } catch (parseError) {
          console.warn('Error al parsear detalles de validación:', parseError)
        }
      } finally {
        this.isLoading = false
        this.isNextLoading = false
      }
    },
  },
})
