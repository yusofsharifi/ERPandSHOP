// Simple mock API for development environment
// Intercepts fetch requests to /api/* and returns simulated responses

type Fetch = typeof window.fetch

const originalFetch: Fetch = window.fetch.bind(window)

interface MockUser {
  id: string
  email: string
  name: string
  role: string
  avatar?: string
}

const DEV_USERS: Record<string, { password: string; user: MockUser; twoFactor?: boolean }> = {
  'admin@bizgenius.local': {
    password: 'Admin1234!',
    user: {
      id: 'dev-admin-1',
      email: 'admin@bizgenius.local',
      name: 'Admin User',
      role: 'Admin',
      avatar: '',
    },
  },
  '2fa@bizgenius.local': {
    password: 'TwoFA123!',
    twoFactor: true,
    user: {
      id: 'dev-2fa-1',
      email: '2fa@bizgenius.local',
      name: 'TwoFA User',
      role: 'User',
      avatar: '',
    },
  },
}

function createResponse(body: any, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

async function mockFetch(input: RequestInfo, init?: RequestInit) {
  const url = typeof input === 'string' ? input : input.url
  const parsed = new URL(url, window.location.origin)
  const origin = parsed.origin
  const pathname = parsed.pathname

  // Only intercept same-origin /api requests. Pass through everything else immediately.
  if (origin !== window.location.origin || !pathname.startsWith('/api')) {
    try {
      return await originalFetch(input, init)
    } catch (err) {
      console.warn('External fetch failed, returning empty response', err)
      return new Response(null, { status: 204 })
    }
  }

  try {
    // Simulate network latency for mocked API calls
    await new Promise((res) => setTimeout(res, 300))

    // Login endpoint
    if (pathname === '/api/auth/login' && init?.method?.toUpperCase() === 'POST') {
      const bodyText = init.body ? String(init.body) : ''
      let body
      try {
        body = JSON.parse(bodyText)
      } catch {
        body = {}
      }
      const { email, password } = body || {}

      const record = DEV_USERS[email]
      if (!record) {
        return createResponse({ detail: 'Invalid credentials' }, 401)
      }

      if (record.password !== password) {
        return createResponse({ detail: 'Invalid credentials' }, 401)
      }

      if (record.twoFactor) {
        // Indicate 2FA required
        return createResponse({ detail: '2FA_REQUIRED' }, 403)
      }

      return createResponse({ access_token: 'dev-token-' + email, user: record.user }, 200)
    }

    // 2FA verify endpoint
    if (pathname === '/api/auth/2fa/verify' && init?.method?.toUpperCase() === 'POST') {
      const bodyText = init.body ? String(init.body) : ''
      let body
      try {
        body = JSON.parse(bodyText)
      } catch {
        body = {}
      }
      const { email, code } = body || {}
      const record = DEV_USERS[email]
      if (!record || !record.twoFactor) {
        return createResponse({ detail: 'Invalid request' }, 400)
      }
      // Accept code '123456' as valid
      if (code === '123456') {
        return createResponse({ access_token: 'dev-token-' + email, user: record.user }, 200)
      }
      return createResponse({ detail: 'Invalid 2FA code' }, 401)
    }

    // Verify token endpoint
    if (pathname === '/api/auth/verify') {
      const auth = init?.headers ? (init.headers as any)['Authorization'] || (init.headers as any)['authorization'] : null
      if (!auth) return createResponse({ detail: 'Missing token' }, 401)
      const token = String(auth).replace('Bearer ', '')
      // token format: dev-token-email
      if (token.startsWith('dev-token-')) {
        const email = token.replace('dev-token-', '')
        const record = DEV_USERS[email]
        if (record) return createResponse({ ok: true }, 200)
      }
      return createResponse({ detail: 'Invalid token' }, 401)
    }

    // Users endpoints: list, create, update, delete
    // In-memory users store
    if (!(window as any).__DEV_USERS_STORE) {
      const initialUsers = Object.values(DEV_USERS).map((r, idx) => ({
        id: `user-${idx + 1}`,
        name: r.user.name,
        email: r.user.email,
        role: r.user.role || 'User',
        status: 'Active',
      }))
      ;(window as any).__DEV_USERS_STORE = initialUsers
    }
    const USERS_STORE: any[] = (window as any).__DEV_USERS_STORE

    // GET /api/users
    if (pathname === '/api/users' && (!init?.method || init.method.toUpperCase() === 'GET')) {
      const urlObj = new URL(url, window.location.origin)
      const search = urlObj.searchParams.get('search') || ''
      const role = urlObj.searchParams.get('role') || ''
      const status = urlObj.searchParams.get('status') || ''
      const page = parseInt(urlObj.searchParams.get('page') || '1')
      const per_page = parseInt(urlObj.searchParams.get('per_page') || '10')

      let filtered = USERS_STORE.slice()
      if (search) {
        const q = search.toLowerCase()
        filtered = filtered.filter(u => u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q))
      }
      if (role) filtered = filtered.filter(u => u.role === role)
      if (status) filtered = filtered.filter(u => u.status === status)

      const total = filtered.length
      const start = (page - 1) * per_page
      const paged = filtered.slice(start, start + per_page)

      return createResponse({ data: paged, meta: { total, page, per_page } }, 200)
    }

    // POST /api/users - create
    if (pathname === '/api/users' && init?.method?.toUpperCase() === 'POST') {
      const bodyText = init.body ? String(init.body) : '{}'
      let body
      try {
        body = JSON.parse(bodyText)
      } catch {
        body = {}
      }
      const id = `user-${USERS_STORE.length + 1}`
      const newUser = {
        id,
        name: body.name,
        email: body.email,
        role: body.role || 'User',
        status: body.status || 'Active',
      }
      USERS_STORE.unshift(newUser)
      return createResponse(newUser, 201)
    }

    // DELETE /api/users/:id
    if (pathname.startsWith('/api/users/') && init?.method?.toUpperCase() === 'DELETE') {
      const id = pathname.split('/').pop()
      const idx = USERS_STORE.findIndex(u => u.id === id)
      if (idx === -1) return createResponse({ detail: 'Not found' }, 404)
      USERS_STORE.splice(idx, 1)
      return createResponse({ ok: true }, 200)
    }

    // PUT /api/users/:id
    if (pathname.startsWith('/api/users/') && init?.method?.toUpperCase() === 'PUT') {
      const id = pathname.split('/').pop()
      const bodyText = init.body ? String(init.body) : '{}'
      let body
      try {
        body = JSON.parse(bodyText)
      } catch {
        body = {}
      }
      const idx = USERS_STORE.findIndex(u => u.id === id)
      if (idx === -1) return createResponse({ detail: 'Not found' }, 404)
      USERS_STORE[idx] = { ...USERS_STORE[idx], ...body }
      return createResponse(USERS_STORE[idx], 200)
    }

    // Fallback to real fetch for other endpoints
    return originalFetch(input, init)
  } catch (err) {
    return originalFetch(input, init)
  }
}

// Install mock only in development
if (import.meta.env.DEV) {
  // @ts-ignore
  window.fetch = mockFetch
  console.info('Mock API installed (development only)')
}

export {}
