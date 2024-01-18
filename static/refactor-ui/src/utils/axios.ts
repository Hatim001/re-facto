import axios, { AxiosResponse } from "axios";
import Cookies from "js-cookie";

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "x-CSRFToken";

let URL: any = "http://localhost:8000"
if (process.env.REACT_APP_ENVIRONMENT === "PROD") {
  URL = process.env.REACT_APP_BACKEND_URL
}

const instance = axios.create({
  baseURL: URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 300000,
});

// Optional: Add request/response interceptors to handle global configurations, error handling, etc.
instance.interceptors.request.use(
  (config: any) => {
    const csrfToken = Cookies.get("csrftoken");
    config.headers["X-CSRFToken"] = csrfToken;
    // Include the CSRF token in the headers of all Axios requests
    // You can add common headers, authentication tokens, etc., to the request here
    return config;
  },
  (error) => {
    // Handle request errors (e.g., network error)
    return Promise.reject(error);
  }
);

instance.interceptors.response.use(
  (response: AxiosResponse) => {
    // You can handle successful responses here
    return response;
  },
  (error) => {
    // Handle response errors (e.g., HTTP errors, error messages from the server)
    return Promise.reject(error);
  }
);

const GET = (url: string, options?: any) => {
  return instance.get(url, options);
};

const POST = (url: string, data?: any, options?: any) => {
  return instance.post(url, data, options);
};

const PUT = (url: string, data?: any, options?: any) => {
  return instance.put(url, data, options);
};

const PATCH = (url: string, data?: any, options?: any) => {
  return instance.patch(url, data, options);
};

const DELETE = (url: string, options?: any) => {
  return instance.delete(url, options);
};

export { GET, POST, PUT, DELETE, PATCH, axios };
