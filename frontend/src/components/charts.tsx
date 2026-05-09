'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  Cell,
} from 'recharts';

const threatCategoryData = [
  { name: 'Phishing', count: 120, color: '#00FFC6' },
  { name: 'Malware', count: 85, color: '#3B82F6' },
  { name: 'Ransomware', count: 40, color: '#EF4444' },
  { name: 'DDoS', count: 25, color: '#F59E0B' },
  { name: 'Insider', count: 15, color: '#A855F7' },
];

const riskTrendData = [
  { time: '00:00', score: 45 },
  { time: '04:00', score: 55 },
  { time: '08:00', score: 60 },
  { time: '12:00', score: 40 },
  { time: '16:00', score: 75 },
  { time: '20:00', score: 50 },
  { time: '24:00', score: 45 },
];

const chartVariants = {
  hidden: { opacity: 0, scale: 0.98 },
  show: { opacity: 1, scale: 1, transition: { duration: 0.6, ease: "easeOut" as const } }
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-background/90 backdrop-blur-xl border border-border/50 p-4 rounded-xl shadow-2xl ring-1 ring-white/10">
        <p className="text-muted-foreground text-[10px] mb-2 font-bold uppercase tracking-[0.2em]">{label}</p>
        <div className="flex items-center gap-2">
          <div 
            className="w-1 h-4 rounded-full" 
            style={{ backgroundColor: payload[0].color || payload[0].fill }} 
          />
          <p className="text-foreground text-lg font-mono font-bold leading-none">
            {payload[0].value}
          </p>
        </div>
      </div>
    );
  }
  return null;
};

export function DashboardCharts() {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <motion.div variants={chartVariants} initial="hidden" animate="show" transition={{ delay: 0.2 }}>
        <Card className="col-span-1 border-border/50 bg-card/40 backdrop-blur-md shadow-lg overflow-hidden group">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Threat Categories
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart 
                  data={threatCategoryData} 
                  margin={{ top: 20, right: 10, left: -25, bottom: 0 }}
                  barSize={40}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                  <XAxis 
                    dataKey="name" 
                    tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10, fontWeight: 500 }} 
                    axisLine={false}
                    tickLine={false}
                    dy={10}
                  />
                  <YAxis 
                    tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10, fontWeight: 500 }}
                    axisLine={false}
                    tickLine={false}
                    dx={-10}
                  />
                  <Tooltip 
                    content={<CustomTooltip />} 
                    cursor={{ fill: 'rgba(255,255,255,0.05)', radius: 8 }} 
                  />
                  <Bar 
                    dataKey="count" 
                    radius={[8, 8, 2, 2]} 
                    animationDuration={2000}
                    animationBegin={300}
                  >
                    {threatCategoryData.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={entry.color} 
                        className="transition-all duration-300 hover:opacity-80 hover:filter hover:brightness-125"
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={chartVariants} initial="hidden" animate="show" transition={{ delay: 0.3 }}>
        <Card className="col-span-1 border-border/50 bg-card/40 backdrop-blur-md shadow-lg overflow-hidden">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              Risk Score Trends (24h)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={riskTrendData} margin={{ top: 20, right: 10, left: -25, bottom: 0 }}>
                  <defs>
                    <linearGradient id="blueGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.45}/>
                      <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.02}/>
                    </linearGradient>
                    <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
                      <feGaussianBlur stdDeviation="5" result="blur" />
                      <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                  <XAxis 
                    dataKey="time" 
                    tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10, fontWeight: 500 }}
                    axisLine={false}
                    tickLine={false}
                    dy={10}
                  />
                  <YAxis 
                    tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10, fontWeight: 500 }}
                    axisLine={false}
                    tickLine={false}
                    domain={[0, 100]}
                    dx={-10}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Area 
                    type="monotone" 
                    dataKey="score" 
                    stroke="#3B82F6" 
                    fill="url(#blueGradient)"
                    strokeWidth={4}
                    animationDuration={2500}
                    activeDot={{ r: 6, fill: "#3B82F6", stroke: "#fff", strokeWidth: 2, className: "shadow-lg" }}
                    style={{ filter: 'url(#softGlow)' }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
