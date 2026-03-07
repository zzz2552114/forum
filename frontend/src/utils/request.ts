import axios from 'axios'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import { ElMessage } from 'element-plus'

// Configure NProgress
NProgress.configure({ showSpinner: false, speed: 400 })

const service = axios.create({
  baseURL: '/api/v1',
  timeout: 10000
})

// Request Interceptor
service.interceptors.request.use(
  config => {
    NProgress.start()
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    NProgress.done()
    return Promise.reject(error)
  }
)

// Response Interceptor
service.interceptors.response.use(
  response => {
    NProgress.done()
    const res = response.data
    // Since our backend uses a unified ResponseBase format: {code, message, data}
    // and HTTP exceptions return something similar or valid HTTP status codes
    if (res.code && res.code !== 0) {
      ElMessage.error(res.message || 'Error occurred')
      return Promise.reject(new Error(res.message || 'Error'))
    }
    return res.data !== undefined ? res.data : res
  },
  error => {
    NProgress.done()
    // Do NOT show ElMessage here — let the calling code handle user-facing error messages
    // to avoid double-popup (interceptor + catch block both showing toast).
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default service
