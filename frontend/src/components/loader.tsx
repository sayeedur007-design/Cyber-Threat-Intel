'use client';

import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

interface LoaderProps {
  text?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function Loader({ text = 'Loading...', className, size = 'md' }: LoaderProps) {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-12 w-12',
    lg: 'h-20 w-20',
  };

  return (
    <div className={cn('flex flex-col items-center justify-center space-y-6 p-8', className)}>
      <div className={cn('relative flex items-center justify-center', sizeClasses[size])}>
        <motion.div 
          animate={{ scale: [1, 2], opacity: [0.8, 0] }}
          transition={{ repeat: Infinity, duration: 1.5, ease: "easeOut" }}
          className="absolute inset-0 border-2 border-primary rounded-full"
        />
        <motion.div 
          animate={{ scale: [1, 2.5], opacity: [0.5, 0] }}
          transition={{ repeat: Infinity, duration: 1.5, ease: "easeOut", delay: 0.5 }}
          className="absolute inset-0 border border-primary/50 rounded-full"
        />
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
          className="absolute inset-0 border-2 border-transparent border-t-primary border-r-primary/50 rounded-full drop-shadow-[0_0_8px_rgba(0,255,198,0.5)]"
        />
        <div className="absolute inset-2 bg-primary/20 rounded-full blur-sm" />
      </div>
      {text && (
        <motion.p 
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
          className="text-sm font-bold tracking-widest uppercase text-primary/80"
        >
          {text}
        </motion.p>
      )}
    </div>
  );
}

