"use client";

import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { authApi } from "@/lib/api";

interface User {
  id: string;
  name: string;
  email: string;
  team_id?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { name: string; email: string; password: string; team_name: string }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem("scout_token");
    if (token) {
      authApi
        .me(token)
        .then((userData) => {
          setUser(userData);
        })
        .catch(() => {
          localStorage.removeItem("scout_token");
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authApi.login(email, password);
    localStorage.setItem("scout_token", response.token);
    setUser(response.user);
  };

  const register = async (data: { name: string; email: string; password: string; team_name: string }) => {
    const response = await authApi.register(data);
    localStorage.setItem("scout_token", response.token);
    setUser(response.user);
  };

  const logout = () => {
    localStorage.removeItem("scout_token");
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
