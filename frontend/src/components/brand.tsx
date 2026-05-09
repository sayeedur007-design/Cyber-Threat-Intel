'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface LogoProps {
  className?: string;
  isCollapsed?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export function Logo({ className, isCollapsed = false, size = 'md' }: LogoProps) {
  const iconSizes = {
    sm: 'h-6 w-6',
    md: 'h-10 w-10',
    lg: 'h-16 w-16'
  };

  return (
    <div className={cn("flex items-center gap-3 group", className)}>
      {/* The Emblem */}
      <div className={cn(
        "relative flex items-center justify-center shrink-0 transition-all duration-500",
        iconSizes[size],
        "bg-primary/5 rounded-xl border border-primary/20 group-hover:bg-primary/10 group-hover:border-primary/40 group-hover:shadow-[0_0_20px_rgba(0,245,212,0.15)]",
        "before:absolute before:inset-0 before:bg-primary/5 before:rounded-xl before:blur-xl before:opacity-0 group-hover:before:opacity-100 before:transition-opacity"
      )}>
        <svg
          viewBox="0 0 100 100"
          className="w-full h-full p-1.5 text-primary"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Outer Grid Nodes */}
          <motion.path
            d="M50 10 L85 30 L85 70 L50 90 L15 70 L15 30 Z"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeOpacity="0.3"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, ease: "easeInOut" }}
          />
          <circle cx="50" cy="10" r="2" fill="currentColor" />
          <circle cx="85" cy="30" r="2" fill="currentColor" />
          <circle cx="85" cy="70" r="2" fill="currentColor" />
          <circle cx="50" cy="90" r="2" fill="currentColor" />
          <circle cx="15" cy="70" r="2" fill="currentColor" />
          <circle cx="15" cy="30" r="2" fill="currentColor" />

          {/* Inner Rings */}
          <circle cx="50" cy="50" r="30" stroke="currentColor" strokeWidth="1" strokeOpacity="0.1" />
          <motion.circle 
            cx="50" cy="50" r="25" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeDasharray="40 120"
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 10, ease: "linear" }}
          />

          {/* Central 'C' and Pulse */}
          <path 
            d="M65 40 A18 18 0 1 0 65 60" 
            stroke="currentColor" 
            strokeWidth="4" 
            strokeLinecap="round" 
          />
          <motion.path
            d="M45 50 H50 L53 40 L57 60 L60 50 H65"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            animate={{ 
              d: [
                "M45 50 H50 L53 40 L57 60 L60 50 H65",
                "M45 50 H50 L53 45 L57 55 L60 50 H65",
                "M45 50 H50 L53 40 L57 60 L60 50 H65"
              ]
            }}
            transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }}
          />
        </svg>

        {/* Ambient Glow */}
        <div className="absolute inset-0 rounded-xl bg-primary/5 group-hover:bg-primary/10 transition-colors pointer-events-none" />
      </div>

      {/* Brand Text */}
      {!isCollapsed && (
        <div className="flex flex-col">
          <motion.span 
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-lg font-black tracking-tighter text-slate-100 leading-none uppercase"
          >
            CTI <span className="text-primary">Analyst</span>
          </motion.span>
          <motion.span 
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="text-[10px] font-black tracking-[0.4em] text-muted-foreground/60 uppercase mt-0.5 leading-none"
          >
            Platform
          </motion.span>
        </div>
      )}
    </div>
  );
}

export function SidebarBranding({ isCollapsed }: { isCollapsed: boolean }) {
  return (
    <div className={cn(
      "px-6 py-8 border-b border-border/40 transition-all duration-300",
      isCollapsed ? "px-4 justify-center" : "px-6"
    )}>
      <Link href="/" className="block">
        <Logo isCollapsed={isCollapsed} />
      </Link>
    </div>
  );
}
