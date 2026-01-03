export const environment = {
  production: false,
  apiUrl: 'http://localhost/api',  // Via nginx
  // apiUrl: 'http://localhost:8000/api',  // Direto (dev)
  mediasBasePath: 'http://localhost:8089',
  useMockData: false,
  defaultUasg: '787010',
  features: {
    contratos: true,
    atas: false,  // Implementar depois
    backup: true,
    reports: true
  }
};
