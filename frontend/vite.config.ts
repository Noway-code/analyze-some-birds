export default {
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/videos': 'http://localhost:8000'
    }
  }
}
