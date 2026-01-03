export const environment = {
  production: true,
  apiUrl: '/api',  // Relativo (via nginx)
  mediasBasePath: 'https://licitacao360.com/midias',
  useMockData: false,
  defaultUasg: '787010',
  features: {
    contratos: true,
    atas: false,
    backup: true,
    reports: true
  }
};