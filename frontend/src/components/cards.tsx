'use client';

import { useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ShieldAlert, Activity, Bug, FileText } from 'lucide-react';
import { motion, useInView, useAnimation } from 'framer-motion';
import { ResponsiveContainer, AreaChart, Area } from 'recharts';
import { cn } from '@/lib/utils';

// Dummy data for mini sparklines
const sparklineData1 = [{ v: 10 }, { v: 15 }, { v: 8 }, { v: 24 }, { v: 20 }, { v: 35 }, { v: 30 }];
const sparklineData2 = [{ v: 5 }, { v: 8 }, { v: 12 }, { v: 4 }, { v: 15 }, { v: 10 }, { v: 24 }];

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: 'spring' as const, stiffness: 300, damping: 24 } }
};

function AnimatedCounter({ value }: { value: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const isInView = useInView(ref, { once: true });
  
  useEffect(() => {
    if (!isInView || !ref.current) return;
    
    let startTimestamp: number | null = null;
    const duration = 1500;
    
    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      // easeOutExpo
      const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      
      if (ref.current) {
        ref.current.textContent = Math.floor(easeProgress * value).toLocaleString();
      }
      
      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };
    
    window.requestAnimationFrame(step);
  }, [value, isInView]);

  return <span ref={ref}>0</span>;
}

function Sparkline({ data, color }: { data: any[], color: string }) {
  return (
    <div className="h-10 w-24 absolute right-4 bottom-4 opacity-40">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id={`sparkGradient-${color}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.8}/>
              <stop offset="95%" stopColor={color} stopOpacity={0}/>
            </linearGradient>
          </defs>
          <Area type="monotone" dataKey="v" stroke={color} fill={`url(#sparkGradient-${color})`} strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function DashboardCards() {
  return (
    <motion.div 
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="grid gap-6 md:grid-cols-2 lg:grid-cols-4"
    >
      <motion.div variants={itemVariants} whileHover={{ y: -5, transition: { duration: 0.2 } }}>
        <Card className="relative overflow-hidden group border-border/50 bg-card/60 backdrop-blur-xl shadow-lg hover:shadow-primary/5 transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground group-hover:text-foreground transition-colors">Total Threats</CardTitle>
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
              <ShieldAlert className="h-4 w-4 text-primary" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold tracking-tighter text-foreground">
              <AnimatedCounter value={1248} />
            </div>
            <p className="text-xs text-primary/80 font-medium mt-1">+12% from last month</p>
            <Sparkline data={sparklineData1} color="hsl(var(--primary))" />
          </CardContent>
        </Card>
      </motion.div>
      
      <motion.div variants={itemVariants} whileHover={{ y: -5, transition: { duration: 0.2 } }}>
        <Card className="relative overflow-hidden group border-destructive/20 bg-card/60 backdrop-blur-xl shadow-lg hover:shadow-destructive/10 transition-all duration-300">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-destructive to-transparent opacity-50" />
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground group-hover:text-foreground transition-colors">High Risk Alerts</CardTitle>
            <div className="relative">
              <motion.div 
                animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
                className="absolute inset-0 rounded-full bg-destructive"
              />
              <div className="relative h-8 w-8 rounded-full bg-destructive/10 flex items-center justify-center">
                <Activity className="h-4 w-4 text-destructive" />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold tracking-tighter text-destructive drop-shadow-[0_0_8px_rgba(239,68,68,0.5)]">
              <AnimatedCounter value={24} />
            </div>
            <p className="text-xs text-destructive/80 font-medium mt-1 flex items-center gap-1">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-destructive opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-destructive"></span>
              </span>
              Requires immediate attention
            </p>
            <Sparkline data={sparklineData2} color="hsl(var(--destructive))" />
          </CardContent>
        </Card>
      </motion.div>
      
      <motion.div variants={itemVariants} whileHover={{ y: -5, transition: { duration: 0.2 } }}>
        <Card className="relative overflow-hidden group border-border/50 bg-card/60 backdrop-blur-xl shadow-lg hover:shadow-secondary/5 transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground group-hover:text-foreground transition-colors">CVEs Analyzed</CardTitle>
            <div className="h-8 w-8 rounded-full bg-secondary/10 flex items-center justify-center">
              <Bug className="h-4 w-4 text-secondary" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold tracking-tighter text-foreground">
              <AnimatedCounter value={342} />
            </div>
            <p className="text-xs text-muted-foreground mt-1">Processed today</p>
          </CardContent>
        </Card>
      </motion.div>
      
      <motion.div variants={itemVariants} whileHover={{ y: -5, transition: { duration: 0.2 } }}>
        <Card className="relative overflow-hidden group border-emerald-500/20 bg-card/60 backdrop-blur-xl shadow-lg hover:shadow-emerald-500/10 transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground group-hover:text-foreground transition-colors">System Status</CardTitle>
            <div className="h-8 w-8 rounded-full bg-emerald-500/10 flex items-center justify-center">
              <FileText className="h-4 w-4 text-emerald-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold tracking-tighter text-emerald-500 drop-shadow-[0_0_8px_rgba(16,185,129,0.3)]">
              Healthy
            </div>
            <p className="text-xs text-emerald-500/80 font-medium mt-1">All backend services operational</p>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
