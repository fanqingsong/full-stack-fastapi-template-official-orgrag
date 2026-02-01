import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import { createRouter, RouterProvider } from "@tanstack/react-router"
import { StrictMode } from "react"
import ReactDOM from "react-dom/client"
import { OpenAPI } from "./client"
import { ThemeProvider } from "./components/theme-provider"
import { Toaster } from "./components/ui/sonner"
import "./index.css"
import { routeTree } from "./routeTree.gen"

// Configure the OpenAPI client
OpenAPI.BASE = import.meta.env.VITE_API_URL || ""
OpenAPI.interceptors.request.use((options) => {
  const token = localStorage.getItem("access_token")
  if (token) {
    return {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`,
      },
    }
  }
  return options
})

const handleApiError = (error: Error) => {
  const err = error as {
    status?: number
    response?: { status?: number }
    detail?: string
    message?: string
  }
  const status = err.status || err.response?.status
  const detail = err.detail || err.message

  console.log("API Error:", { status, detail, error: err })

  // Clear token and redirect on auth errors (401, 403)
  if (status && [401, 403].includes(status)) {
    localStorage.removeItem("access_token")
    window.location.href = "/login"
    return
  }

  // Handle "User not found" - check detail message directly since status might be undefined
  if (detail === "User not found" || detail?.toLowerCase().includes("user not found")) {
    localStorage.removeItem("access_token")
    window.location.href = "/login"
    return
  }
}
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: handleApiError,
  }),
  mutationCache: new MutationCache({
    onError: handleApiError,
  }),
})

const router = createRouter({ routeTree })
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router
  }
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
        <Toaster richColors closeButton />
      </QueryClientProvider>
    </ThemeProvider>
  </StrictMode>,
)
