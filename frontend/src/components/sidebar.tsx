'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { LayoutDashboard, MessageSquareText, ShieldCheck, Bug, ChevronLeft, ChevronRight, Menu, History, FileText, UserCircle, LogOut } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/components/AuthProvider';
import { SidebarBranding } from './brand';

const navItems = [
  { title: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { title: 'Reports', href: '/report', icon: FileText },
  { title: 'History', href: '/history', icon: History },
  { title: 'RAG Query', href: '/rag', icon: MessageSquareText },
  { title: 'Classifier', href: '/classifier', icon: ShieldCheck },
  { title: 'Vulnerabilities', href: '/vulnerabilities', icon: Bug },
];

export function Sidebar() {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const { user, logout } = useAuth();

  if (pathname === '/login' || pathname === '/register') return null;

  return (
    <>
      {/* Mobile Menu Toggle Button */}
      <Button
        variant="outline"
        size="icon"
        className="fixed bottom-4 right-4 z-50 md:hidden rounded-full shadow-lg border-primary/20 bg-background/80 backdrop-blur-md"
        onClick={() => setIsMobileOpen(!isMobileOpen)}
      >
        <Menu className="h-5 w-5 text-primary" />
      </Button>

      {/* Sidebar Container */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 border-r border-border/40 bg-background/95 backdrop-blur-xl supports-[backdrop-filter]:bg-background/80 transition-all duration-300 ease-in-out md:relative flex flex-col',
          isCollapsed ? 'md:w-[80px]' : 'md:w-64',
          isMobileOpen ? 'translate-x-0 w-64' : '-translate-x-full md:translate-x-0'
        )}
      >
        <SidebarBranding isCollapsed={isCollapsed} />
        <div className="flex h-full flex-col relative py-6">
          
          {/* Collapse Toggle Button */}
          <Button
            variant="ghost"
            size="icon"
            className="absolute -right-4 top-6 z-50 hidden md:flex h-8 w-8 rounded-full border border-border/50 bg-background shadow-md hover:bg-muted/50 hover:text-primary transition-colors"
            onClick={() => setIsCollapsed(!isCollapsed)}
          >
            <motion.div animate={{ rotate: isCollapsed ? 180 : 0 }} transition={{ duration: 0.3 }}>
              <ChevronLeft className="h-4 w-4" />
            </motion.div>
          </Button>

          <div className="px-4 flex-1 flex flex-col gap-6">
            <div className="px-2 h-6 flex items-center overflow-hidden">
              <AnimatePresence>
                {!isCollapsed && (
                  <motion.h2 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                    className="text-xs font-bold uppercase tracking-widest text-muted-foreground/70 whitespace-nowrap"
                  >
                    Platform Modules
                  </motion.h2>
                )}
              </AnimatePresence>
            </div>
            
            <nav className="space-y-2 relative">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setIsMobileOpen(false)}
                    className="relative block"
                  >
                    <motion.div
                      whileHover={{ scale: 1.02, x: 4 }}
                      whileTap={{ scale: 0.98 }}
                      className={cn(
                        'relative flex items-center rounded-xl text-sm font-medium transition-colors overflow-hidden',
                        isCollapsed ? 'justify-center p-3' : 'gap-4 px-4 py-3',
                        isActive ? 'text-primary' : 'text-muted-foreground hover:text-foreground'
                      )}
                    >
                      {isActive && (
                        <motion.div
                          layoutId="sidebar-active-indicator"
                          className="absolute inset-0 bg-primary/10 border-l-2 border-primary rounded-r-xl"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          exit={{ opacity: 0 }}
                          transition={{ type: "spring" as const, stiffness: 300, damping: 30 }}
                        />
                      )}
                      <item.icon className="relative z-10 h-5 w-5 shrink-0" />
                      
                      <AnimatePresence>
                        {!isCollapsed && (
                          <motion.span 
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -10 }}
                            className="relative z-10 whitespace-nowrap"
                          >
                            {item.title}
                          </motion.span>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Profile & Logout Section */}
          <div className="px-4 mt-auto">
             <div className={cn(
               "flex items-center border-t border-border/50 pt-6 transition-all duration-300",
               isCollapsed ? "justify-center" : "gap-3 px-2"
             )}>
               <div className="h-10 w-10 shrink-0 rounded-full bg-muted/50 flex items-center justify-center border border-border/50">
                 <UserCircle className="h-6 w-6 text-muted-foreground" />
               </div>
               
               <AnimatePresence>
                 {!isCollapsed && (
                   <motion.div 
                     initial={{ opacity: 0, width: 0 }}
                     animate={{ opacity: 1, width: "auto" }}
                     exit={{ opacity: 0, width: 0 }}
                     className="flex-1 overflow-hidden whitespace-nowrap"
                   >
                     <p className="text-sm font-medium text-foreground">{user?.username || 'Analyst'}</p>
                     <p className="text-xs text-muted-foreground truncate">{user?.email || 'SOC Tier 2'}</p>
                   </motion.div>
                 )}
               </AnimatePresence>

               {!isCollapsed && (
                 <Button variant="ghost" size="icon" onClick={logout} className="shrink-0 hover:bg-destructive/10 hover:text-destructive transition-colors">
                   <LogOut className="h-4 w-4" />
                 </Button>
               )}
             </div>
          </div>
        </div>
      </aside>

      {/* Mobile Overlay */}
      <AnimatePresence>
        {isMobileOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-30 bg-background/80 backdrop-blur-sm md:hidden"
            onClick={() => setIsMobileOpen(false)}
          />
        )}
      </AnimatePresence>
    </>
  );
}
