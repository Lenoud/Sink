import { createAuthGateway } from './_auth.mjs'

export default createAuthGateway({ host: 'go.vertflux.com', binding: 'SINK_APP', managementOnly: true, siteTokenBinding: 'SINK_SITE_TOKEN' })
