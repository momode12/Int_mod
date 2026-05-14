const TOKEN_KEY = "token";
const USER_KEY  = "user";

// Token
export const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

export const setToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const removeToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
};

export const isTokenValid = (): boolean => {
  const token = getToken();
  if (!token) return false;

  try {
    // Décode le JWT sans vérification de signature
    const payload = JSON.parse(atob(token.split(".")[1]));
    const expiry   = payload.exp * 1000;
    return Date.now() < expiry;
  } catch {
    return false;
  }
};

// User
export const getSavedUser = <T>(): T | null => {
  try {
    const user = localStorage.getItem(USER_KEY);
    return user ? JSON.parse(user) : null;
  } catch {
    return null;
  }
};

export const saveUser = <T>(user: T): void => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

export const removeUser = (): void => {
  localStorage.removeItem(USER_KEY);
};

// Nettoie tout
export const clearStorage = (): void => {
  removeToken();
  removeUser();
};