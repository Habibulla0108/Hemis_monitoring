// frontend/src/api/http.ts
import axios from "axios";
import { API_BASE_URL } from "../config/env";

// Agar env'dan kelmasa, default qilib backend URL ni qo'yamiz
const baseURL = API_BASE_URL || "http://127.0.0.1:8000/api";

console.log("API_BASE_URL (frontend):", baseURL);

export const http = axios.create({
  baseURL: baseURL,
  timeout: 600000,   // avval 15000 edi, 60 sekund qilamiz
});


http.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("HTTP error:", error);
    return Promise.reject(error);
  }
);

export default http;
