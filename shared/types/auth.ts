export type AuthMethod = 'site-token' | 'access-user' | 'access-service' | 'vertflux-sso'

export interface VerifyResponse {
  name: string
  url: string
  authMethod: AuthMethod
  userID: string
  userEmail: string
  accessEnabled: boolean
}
