'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { DashboardCards } from '@/components/cards';
import dynamic from 'next/dynamic';
import { motion } from 'framer-motion';

const DashboardCharts = dynamic(() => import('@/components/charts').then(mod => mod.DashboardCharts), {
  ssr: false,
  loading: () => <div className="h-[400px] rounded-xl bg-card/40 animate-pulse border border-border/50" />
});

const recentThreats = [
  { id: 'TRT-8921', type: 'Ransomware', severity: 'Critical', timestamp: '2026-05-02 14:22:00' },
  { id: 'TRT-8920', type: 'Phishing', severity: 'High', timestamp: '2026-05-02 13:45:10' },
  { id: 'TRT-8919', type: 'Malware', severity: 'Medium', timestamp: '2026-05-02 12:10:05' },
  { id: 'TRT-8918', type: 'DDoS', severity: 'High', timestamp: '2026-05-02 11:30:00' },
  { id: 'TRT-8917', type: 'Phishing', severity: 'Low', timestamp: '2026-05-02 10:05:00' },
];

const getSeverityVariant = (severity: string) => {
  switch (severity.toLowerCase()) {
    case 'critical': return 'destructive';
    case 'high': return 'destructive';
    case 'medium': return 'default';
    case 'low': return 'secondary';
    default: return 'outline';
  }
};

const getSeverityStyle = (severity: string) => {
  if (severity.toLowerCase() === 'critical' || severity.toLowerCase() === 'high') {
    return 'shadow-[0_0_10px_rgba(239,68,68,0.4)] animate-pulse';
  }
  return '';
};

// Variants for staggered layout
const pageVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.15 } }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: 'spring' as const, stiffness: 300, damping: 24 } }
};

export default function DashboardPage() {
  return (
    <motion.div 
      variants={pageVariants}
      initial="hidden"
      animate="show"
      className="space-y-8 relative"
    >
      {/* Background glow for the header */}
      <div className="absolute top-0 left-1/4 w-1/2 h-32 bg-primary/10 rounded-full blur-[100px] pointer-events-none -z-10" />

      <motion.div variants={itemVariants}>
        <h1 className="text-4xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-foreground to-foreground/70">
          Command Center
        </h1>
        <p className="text-muted-foreground mt-2 text-sm font-medium">
          Real-time threat intelligence overview and tactical risk analysis.
        </p>
      </motion.div>

      <motion.div variants={itemVariants}>
        <DashboardCards />
      </motion.div>

      <motion.div variants={itemVariants}>
        <DashboardCharts />
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card className="border-border/50 bg-card/60 backdrop-blur-xl shadow-lg">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Active Threats</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border border-border/50 overflow-hidden">
              <Table>
                <TableHeader className="bg-muted/30">
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="font-semibold text-muted-foreground">Threat ID</TableHead>
                    <TableHead className="font-semibold text-muted-foreground">Type</TableHead>
                    <TableHead className="font-semibold text-muted-foreground">Severity</TableHead>
                    <TableHead className="text-right font-semibold text-muted-foreground">Timestamp</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {recentThreats.map((threat, index) => (
                    <motion.tr 
                      key={threat.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05, type: "spring" as const, stiffness: 200, damping: 20 }}
                      className="border-b border-border/40 transition-all duration-300 hover:bg-primary/5 hover:shadow-md data-[state=selected]:bg-muted group cursor-pointer relative z-0 hover:z-10"
                    >
                      <TableCell className="font-medium font-mono text-xs">
                        <div className="flex items-center gap-3">
                          <div className={`w-1.5 h-6 rounded-r-full absolute left-0 opacity-0 group-hover:opacity-100 transition-all duration-300 transform scale-y-50 group-hover:scale-y-100 ${threat.severity.toLowerCase() === 'critical' || threat.severity.toLowerCase() === 'high' ? 'bg-destructive shadow-[0_0_10px_rgba(239,68,68,0.8)]' : 'bg-primary shadow-[0_0_10px_rgba(0,255,198,0.5)]'}`} />
                          <span className="pl-2 group-hover:text-primary transition-colors">{threat.id}</span>
                        </div>
                      </TableCell>
                      <TableCell>{threat.type}</TableCell>
                      <TableCell>
                        <Badge variant={getSeverityVariant(threat.severity) as any} className={getSeverityStyle(threat.severity)}>
                          {threat.severity}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right text-muted-foreground text-xs font-mono">
                        {threat.timestamp}
                      </TableCell>
                    </motion.tr>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
