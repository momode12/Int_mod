const BASE_URL = "http://localhost:8000/api";

interface RequestOptions {
  method?:  "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  body?:    unknown;
  headers?: Record<string, string>;
}

// Récupère le token depuis le localStorage
const getAuthHeader = (): Record<string, string> => {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Requête de base
export const request = async <T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> => {
  const { method = "GET", body, headers = {} } = options;

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || "Une erreur est survenue");
  }

  return response.json();
};

// Méthodes utilitaires
export const api = {
  get:    <T>(endpoint: string) =>
    request<T>(endpoint),

  post:   <T>(endpoint: string, body: unknown) =>
    request<T>(endpoint, { method: "POST", body }),

  put:    <T>(endpoint: string, body: unknown) =>
    request<T>(endpoint, { method: "PUT", body }),

  patch:  <T>(endpoint: string, body: unknown) =>
    request<T>(endpoint, { method: "PATCH", body }),

  delete: <T>(endpoint: string) =>
    request<T>(endpoint, { method: "DELETE" }),
};