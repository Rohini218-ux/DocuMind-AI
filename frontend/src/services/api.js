
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(endpoint, options = {}) {
  const token = localStorage.getItem("access_token");

  const headers = new Headers(options.headers || {});

  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed: ${response.status}`);
  }

  if (response.status === 204) return null;

  return response.json();
}

export const api = {
  register(data) {
    return request("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async login(data) {
    const result = await request("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });

    // Support common OAuth2 and JSON token response formats.
    const token =
      result.access_token ??
      result.token ??
      result.accessToken;

    if (!token) {
      throw new Error(
        "Login succeeded, but the response did not contain an access token."
      );
    }

    localStorage.setItem("access_token", token);
    return result;
  },

  getDocuments() {
    return request("/documents");
  },

  uploadDocument(file) {
    const formData = new FormData();
    formData.append("file", file);

    return request("/documents/upload", {
      method: "POST",
      body: formData,
    });
  },

  askQuestion(question, topK = 3) {
    return request("/chat/ask", {
      method: "POST",
      body: JSON.stringify({
        question,
        top_k: topK,
      }),
    });
  },

  logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("token");
  },
};
