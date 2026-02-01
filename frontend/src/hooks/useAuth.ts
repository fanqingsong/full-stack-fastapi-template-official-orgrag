import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"

import {
  LoginService,
  UsersService,
  type Body_login_login_access_token as AccessToken,
  type UserPublic,
  type UserRegister,
} from "@/client"
import { handleError } from "@/utils"
import useCustomToast from "./useCustomToast"

const isLoggedIn = () => {
  return localStorage.getItem("access_token") !== null
}

const useAuth = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()

  const { data: user } = useQuery<UserPublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: async () => {
      try {
        return await UsersService.readUserMe()
      } catch (error) {
        const err = error as { detail?: string; status?: number }
        // Handle authentication errors (401, 403)
        if (err.status === 401 || err.status === 403 ||
            err.detail === "Could not validate credentials" ||
            err.detail?.includes("not authenticated") ||
            err.detail?.includes("Not authenticated")) {
          // Clear the invalid token immediately
          localStorage.removeItem("access_token")
          queryClient.setQueryData(["currentUser"], null)
          // Redirect to login if not already there
          if (window.location.pathname !== "/login") {
            navigate({ to: "/login" })
          }
          return null
        }
        throw error
      }
    },
    enabled: isLoggedIn(),
    retry: false,
  })

  const signUpMutation = useMutation({
    mutationFn: (data: UserRegister) =>
      UsersService.registerUser({ requestBody: data }),
    onSuccess: () => {
      navigate({ to: "/login" })
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

  const login = async (data: AccessToken) => {
    const response = await LoginService.loginAccessToken({ formData: data })
    localStorage.setItem("access_token", response.access_token)
  }

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: async () => {
      // Invalidate and refetch user data immediately after login
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      navigate({ to: "/" })
    },
    onError: handleError.bind(showErrorToast),
  })

  const logout = () => {
    localStorage.removeItem("access_token")
    navigate({ to: "/login" })
  }

  return {
    signUpMutation,
    loginMutation,
    logout,
    user,
  }
}

export { isLoggedIn }
export default useAuth
