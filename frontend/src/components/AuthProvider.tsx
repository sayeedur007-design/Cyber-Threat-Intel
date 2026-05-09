'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { ctiApi } from '@/services/api';
import { Loader } from '@/components/loader';

interface User {
  username: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const PUBLIC_ROUTES = ['/login', '/register'];

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      
      if (!token) {
        if (!PUBLIC_ROUTES.includes(pathname)) {
          router.push('/login');
        }
        setIsLoading(false);
        return;
      }

      try {
        const userData = await ctiApi.getMe();
        setUser(userData);
        if (PUBLIC_ROUTES.includes(pathname)) {
          router.push('/dashboard');
        }
      } catch (error) {
        // Token is invalid or expired
        localStorage.removeItem('token');
        if (!PUBLIC_ROUTES.includes(pathname)) {
          router.push('/login');
        }
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, [pathname, router]);

  const login = (token: string) => {
    localStorage.setItem('token', token);
    router.push('/dashboard');
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    router.push('/login');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader text="Verifying session..." size="lg" />
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
