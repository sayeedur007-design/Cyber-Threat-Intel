'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ShieldCheck, AlertCircle, Database, Cpu, Activity, Sparkles } from 'lucide-react';
import { ctiApi } from '@/services/api';
import { motion, AnimatePresence } from 'framer-motion';
import type { Variants } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface ClassificationResult {
  category: string;
  confidence: number;
  probabilities: Record<string, number>;
}

// Processing Animation Component
const processingSteps = [
  { text: 'Analyzing Threat Data...', icon: Database },
  { text: 'Running Correlation Engine...', icon: Cpu },
  { text: 'Generating Confidence Score...', icon: Activity },
];

function ProcessingState() {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const timer1 = setTimeout(() => setStep(1), 1000);
    const timer2 = setTimeout(() => setStep(2), 2000);
    return () => { clearTimeout(timer1); clearTimeout(timer2); };
  }, []);

  const CurrentIcon = processingSteps[step].icon;

  return (
    <div className="h-[350px] flex flex-col items-center justify-center space-y-8 bg-card/40 rounded-xl border border-border/30 backdrop-blur-sm relative overflow-hidden">
      {/* Background ambient glow */}
      <motion.div
        animate={{ scale: [1, 1.1, 1], opacity: [0.1, 0.2, 0.1] }}
        transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
        className="absolute inset-0 bg-primary/5 rounded-full blur-[100px] pointer-events-none"
      />
      
      <div className="relative z-10">
        <motion.div
          animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.8, 0.3] }}
          transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
          className="absolute inset-0 bg-primary/20 rounded-full blur-xl"
        />
        <div className="relative h-20 w-20 bg-background/80 backdrop-blur-md border border-primary/30 rounded-full flex items-center justify-center shadow-[0_0_20px_rgba(0,255,198,0.2)]">
          <CurrentIcon className="h-10 w-10 text-primary" />
        </div>
      </div>
      
      <div className="h-8 overflow-hidden z-10">
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            transition={{ duration: 0.3 }}
            className="text-sm font-bold text-primary tracking-[0.2em] uppercase"
          >
            {processingSteps[step].text}
          </motion.div>
        </AnimatePresence>
      </div>
      
      {/* Progress Bar */}
      <div className="w-56 h-1.5 bg-muted/50 rounded-full overflow-hidden z-10 backdrop-blur-sm">
        <motion.div 
          className="h-full bg-primary shadow-[0_0_10px_rgba(0,255,198,0.5)]"
          initial={{ width: "0%" }}
          animate={{ width: `${((step + 1) / 3) * 100}%` }}
          transition={{ duration: 0.8, ease: "easeInOut" }}
        />
      </div>
    </div>
  );
}

// Idle Empty State Component
function EmptyState() {
  return (
    <div className="h-[350px] flex flex-col items-center justify-center text-muted-foreground border-2 border-dashed border-border/40 rounded-xl bg-card/20 relative overflow-hidden group transition-colors hover:border-primary/20 hover:bg-card/40">
      <motion.div
        animate={{ scale: [1, 1.05, 1], opacity: [0.05, 0.1, 0.05] }}
        transition={{ repeat: Infinity, duration: 4 }}
        className="absolute w-64 h-64 bg-primary/20 rounded-full blur-3xl pointer-events-none"
      />
      <ShieldCheck className="h-14 w-14 mb-5 text-muted-foreground/40 group-hover:text-primary/40 transition-colors duration-500" />
      <p className="text-sm font-bold tracking-[0.15em] text-foreground/70 uppercase">Awaiting Threat Data</p>
      <p className="text-xs opacity-60 mt-2 font-medium">System idle. Ready for analysis.</p>
    </div>
  );
}

// Recharts Custom Tooltip
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-background/90 backdrop-blur-xl border border-border/50 p-3 rounded-lg shadow-2xl">
        <p className="text-muted-foreground text-xs mb-1 font-medium uppercase tracking-wider">{label}</p>
        <p className="text-foreground text-sm font-bold flex items-center">
          <span className="inline-block w-2.5 h-2.5 rounded-full mr-2" style={{ backgroundColor: payload[0].payload.color }} />
          {payload[0].value}% Probability
        </p>
      </div>
    );
  }
  return null;
};

// Variants
const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } }
};


const itemVariants={
  hidden:{
    opacity:0,
    y:15
  },
  show:{
    opacity:1,
    y:0,
    transition:{
      type:"spring" as "spring",
      stiffness:300,
      damping:24
    }
  }
} as const;

export default function ClassifierPage() {
  const [text, setText] = useState('');
  const [isClassifying, setIsClassifying] = useState(false);
  const [result, setResult] = useState<ClassificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleClassify = async () => {
    if (!text.trim()) return;
    
    setIsClassifying(true);
    setError(null);
    setResult(null);
    try {
      // Artificial delay to guarantee premium staged animation visibility
      const [response] = await Promise.all([
        ctiApi.classifyText(text),
        new Promise(resolve => setTimeout(resolve, 3000))
      ]);
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Classification failed');
    } finally {
      setIsClassifying(false);
    }
  };

  const categoryColors: Record<string, string> = {
    malware: '#00F5D4',
    benign: '#4CC9F0',
    phishing: '#F72585',
    ransomware: '#F77F00',
    default: '#3B82F6'
  };

  const chartData = result 
    ? Object.entries(result.probabilities)
        .map(([name, prob]) => {
          const lowerName = name.toLowerCase();
          return {
            name: name.charAt(0).toUpperCase() + name.slice(1),
            probability: Math.round(prob * 100),
            color: categoryColors[lowerName] || categoryColors.default,
          };
        })
        .sort((a, b) => b.probability - a.probability)
    : [];

  const getConfidenceGlow = (confidence: number) => {
    if (confidence >= 0.8) return 'shadow-[0_0_30px_rgba(0,245,212,0.25)] border-[#00F5D4]/40';
    if (confidence >= 0.5) return 'shadow-[0_0_30px_rgba(76,201,240,0.2)] border-[#4CC9F0]/30';
    return 'shadow-[0_0_30px_rgba(247,37,133,0.15)] border-[#F72585]/20';
  };

  return (
    <div className="space-y-8 relative">
      {/* Background glow for the header */}
      <div className="absolute top-0 left-0 w-1/3 h-40 bg-secondary/10 rounded-full blur-[120px] pointer-events-none -z-10" />

      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <h1 className="text-4xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-slate-50 to-slate-400 uppercase">
          Threat <span className="text-primary">Classifier</span>
        </h1>
        <p className="text-muted-foreground mt-2 text-sm font-medium flex items-center gap-2">
          <Activity className="w-4 h-4 text-primary" />
          Tactical machine learning engine for real-time intelligence categorization.
        </p>
      </motion.div>

      <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-5">
        {/* Input Area */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }} 
          animate={{ opacity: 1, x: 0 }} 
          transition={{ duration: 0.5, delay: 0.1 }}
          className="lg:col-span-2"
        >
          <Card className="border-border/50 bg-card/40 backdrop-blur-xl shadow-2xl h-full flex flex-col ring-1 ring-white/5">
            <CardHeader className="pb-4 border-b border-border/40">
              <CardTitle className="flex items-center gap-3 text-sm font-black uppercase tracking-widest text-slate-100">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Database className="w-4 h-4 text-primary" />
                </div>
                Threat Data Input
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6 flex-1 flex flex-col pt-6">
              {error && (
                <Alert variant="destructive" className="bg-destructive/10 border-destructive/20 text-destructive rounded-xl">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription className="text-xs font-bold">{error}</AlertDescription>
                </Alert>
              )}
              <div className="relative flex-1 flex flex-col group">
                <div className="absolute -inset-1 bg-gradient-to-r from-primary/20 to-secondary/20 rounded-2xl blur opacity-0 group-focus-within:opacity-100 transition duration-500" />
                <Textarea
                  placeholder="Paste tactical logs, obfuscated scripts, or raw intelligence reports here..."
                  className="flex-1 min-h-[350px] resize-none relative bg-background/60 border-border/60 focus-visible:ring-primary/40 text-[13px] font-mono leading-relaxed rounded-xl p-4 shadow-inner"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  disabled={isClassifying}
                />
              </div>
              <motion.div whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}>
                <Button
                  className="w-full h-14 relative overflow-hidden group shadow-[0_0_20px_rgba(0,255,198,0.15)] rounded-xl bg-primary text-primary-foreground"
                  onClick={handleClassify}
                  disabled={isClassifying || !text.trim()}
                >
                  <div className="absolute inset-0 w-full h-full bg-white opacity-0 group-hover:opacity-10 transition-opacity duration-300" />
                  {isClassifying ? (
                    <span className="flex items-center font-black tracking-widest text-xs uppercase">
                      <Sparkles className="mr-3 h-4 w-4 animate-spin" />
                      Decrypting Pattern...
                    </span>
                  ) : (
                    <span className="flex items-center font-black tracking-widest text-xs uppercase">
                      <ShieldCheck className="mr-3 h-5 w-5" />
                      Initialize Classification
                    </span>
                  )}
                </Button>
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Results Area */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }} 
          animate={{ opacity: 1, x: 0 }} 
          transition={{ duration: 0.5, delay: 0.2 }}
          className="lg:col-span-3"
        >
          <Card className="border-border/50 bg-card/40 backdrop-blur-xl shadow-2xl h-full flex flex-col ring-1 ring-white/5">
            <CardHeader className="pb-4 border-b border-border/40">
              <CardTitle className="flex items-center gap-3 text-sm font-black uppercase tracking-widest text-slate-100">
                <div className="p-2 bg-secondary/10 rounded-lg">
                  <Activity className="w-4 h-4 text-secondary" />
                </div>
                Analytical Intelligence
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col pt-6">
              {isClassifying ? (
                <ProcessingState />
              ) : !result ? (
                <EmptyState />
              ) : (
                <motion.div 
                  variants={containerVariants} 
                  initial="hidden" 
                  animate="show" 
                  className="space-y-10"
                >
                  {/* Highlight Predicted Result */}
                  <div className="grid gap-6 md:grid-cols-3">
                    <motion.div
  initial={{opacity:0,y:15}}
  animate={{opacity:1,y:0}}
  transition={{
    type:"spring" as const,
    stiffness:300,
    damping:24
  }}
  className={`md:col-span-2 relative p-10 bg-card/40 border rounded-2xl overflow-hidden transition-all duration-700 ${getConfidenceGlow(result.confidence)}`}
>
                      <div className="absolute top-0 right-0 w-48 h-48 bg-primary/10 rounded-full blur-[80px] -mr-16 -mt-16 pointer-events-none" />
                      <div className="flex flex-col relative z-10">
                        <div className="text-[10px] font-black text-muted-foreground/60 mb-4 uppercase tracking-[0.3em]">
                          Threat Classification Output
                        </div>
                        <div className="text-6xl font-black text-slate-50 capitalize tracking-tighter mb-6">
                          {result.category}
                        </div>
                        <div className="flex items-center gap-4">
                          <motion.div 
                            initial={{ width: 0 }} 
                            animate={{ width: 'auto' }} 
                            className="flex items-center gap-2 bg-primary/10 border border-primary/20 rounded-full py-1.5 px-4"
                          >
                            <Sparkles className="w-3.5 h-3.5 text-primary" />
                            <span className="text-xs font-black text-primary uppercase tracking-tighter">
                              {Math.round(result.confidence * 100)}% Confidence
                            </span>
                          </motion.div>
                          <span className="text-[10px] font-bold text-muted-foreground/40 uppercase tracking-widest">
                            Verified by CTI-LLM v4.2
                          </span>
                        </div>
                      </div>
                    </motion.div>

                    {/* Analyst Signals Section */}
                    <motion.div
  initial={{opacity:0,y:15}}
  animate={{opacity:1,y:0}}
  transition={{
    type:"spring" as const,
    stiffness:300,
    damping:24
  }}
  className="bg-white/[0.02] border border-border/40 rounded-2xl p-6 flex flex-col"
>
                      <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground mb-4">Analyst Signals</h4>
                      <div className="space-y-4">
                        <div className="flex items-center gap-3">
                          <div className="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(0,255,198,0.6)]" />
                          <span className="text-[11px] font-bold text-slate-300">Shared C2 infrastructure detected</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(0,255,198,0.6)]" />
                          <span className="text-[11px] font-bold text-slate-300">Malware family overlap observed</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="w-1.5 h-1.5 rounded-full bg-secondary shadow-[0_0_8px_rgba(59,130,246,0.6)]" />
                          <span className="text-[11px] font-bold text-slate-400 italic">No attribution conflict detected</span>
                        </div>
                      </div>
                    </motion.div>
                  </div>

                  {/* Probabilities Bar Chart */}
                  <motion.div
  initial={{opacity:0,y:15}}
  animate={{opacity:1,y:0}}
  transition={{
    type:"spring",
    stiffness:300,
    damping:24
  }}
  className="space-y-6 pt-4"
>
                    <div className="flex items-center justify-between border-b border-border/40 pb-3">
                      <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground">Probability Distribution Grid</h4>
                      <div className="flex gap-4">
                        {Object.entries(categoryColors).filter(([k]) => k !== 'default').map(([name, color]) => (
                          <div key={name} className="flex items-center gap-1.5">
                            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                            <span className="text-[9px] font-bold text-muted-foreground/60 uppercase">{name}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="h-[220px] w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={chartData} layout="vertical" margin={{ top: 0, right: 40, left: 0, bottom: 0 }}>
                          <defs>
                            {chartData.map((entry, index) => (
                              <linearGradient key={`grad-${index}`} id={`grad-${index}`} x1="0" y1="0" x2="1" y2="0">
                                <stop offset="0%" stopColor={entry.color} stopOpacity={0.6}/>
                                <stop offset="100%" stopColor={entry.color} stopOpacity={1}/>
                              </linearGradient>
                            ))}
                            <filter id="barGlow" x="-20%" y="-20%" width="140%" height="140%">
                              <feGaussianBlur stdDeviation="3" result="blur" />
                              <feComposite in="SourceGraphic" in2="blur" operator="over" />
                            </filter>
                          </defs>
                          <CartesianGrid strokeDasharray="4 4" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                          <XAxis 
                            type="number" 
                            domain={[0, 100]} 
                            tickFormatter={(val) => `${val}%`}
                            tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10, fontWeight: 700 }}
                            axisLine={false}
                            tickLine={false}
                            dy={10}
                          />
                          <YAxis 
                            dataKey="name" 
                            type="category" 
                            tick={{ fill: 'rgba(255,255,255,0.8)', fontSize: 11, fontWeight: 800}}
                            axisLine={false}
                            tickLine={false}
                            width={100}
                          />
                          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)', radius: 4 }} />
                          <Bar 
                            dataKey="probability" 
                            radius={[0, 4, 4, 0]} 
                            animationDuration={2000} 
                            barSize={32}
                            className="transition-all duration-300"
                          >
                            {chartData.map((entry, index) => (
                              <Cell 
                                key={`cell-${index}`} 
                                fill={`url(#grad-${index})`} 
                                style={{ filter: entry.probability > 40 ? 'url(#barGlow)' : 'none' }}
                                className="hover:opacity-80 transition-opacity"
                              />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </motion.div>
                </motion.div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
