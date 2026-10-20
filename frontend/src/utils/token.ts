/** 访问令牌的本地校验（仅解析，不验签，服务端才是权威） */

interface JwtPayload {
  exp?: number
  sub?: string
  role?: string
}

/** 解析 JWT 负载；解析失败返回 null */
export function decodeToken(token: string | null): JwtPayload | null {
  if (!token) return null
  const parts = token.split('.')
  const payload = parts[1]
  if (!payload) return null
  try {
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
    const padded = normalized.padEnd(normalized.length + ((4 - (normalized.length % 4)) % 4), '=')
    return JSON.parse(atob(padded)) as JwtPayload
  } catch {
    return null
  }
}

/** 令牌是否已过期（按 exp 判断；无法解析时视为有效，交由服务端裁决） */
export function isTokenExpired(token: string | null): boolean {
  const payload = decodeToken(token)
  if (!payload?.exp) return false
  return payload.exp * 1000 <= Date.now()
}
