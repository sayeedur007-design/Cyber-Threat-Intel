'use client';

import { useAuth } from '@/components/AuthProvider';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { Logo } from './brand';

export function Navbar() {
  const { user } = useAuth();
  const pathname = usePathname();

  // Hide navbar on auth routes
  if (pathname === '/login' || pathname === '/register') return null;

  return (
    <header className="sticky top-0 z-50 flex h-16 w-full items-center justify-between border-b border-border/40 bg-background/80 px-6 backdrop-blur-md supports-[backdrop-filter]:bg-background/60 shadow-[0_4px_30px_rgba(0,0,0,0.1)] transition-all duration-300">
      <Link href="/">
        <Logo size="sm" className="scale-90 origin-left" />
      </Link>
      <div className="flex items-center gap-4">
        {/* Simplified right side, removing redundant user profile and logout controls */}
        {!user && (
          <div className="text-sm text-muted-foreground font-medium flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-destructive animate-pulse" />
            Authentication Required
          </div>
        )}
      </div>
    </header>
  );
}
