'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Search, Loader2, AlertCircle, ShieldAlert, CheckCircle2, ServerCrash, Activity, Fingerprint, Bug, Shield } from 'lucide-react';
import { ctiApi } from '@/services/api';
import { motion, AnimatePresence } from 'framer-motion';

interface VulnerabilityData {
  id: string;
  description: string;
  cvss_score: number;
  severity: string;
  mitigation?: string;
}

const CVSSGauge = ({ score }: { score: number }) => {
  const percentage = (score / 10) * 100;
  const color = score >= 9 ? 'text-red-500' : score >= 7 ? 'text-orange-500' : score >= 4 ? 'text-yellow-500' : 'text-green-500';
  
  return (
    <div className="relative w-28 h-28 flex items-center justify-center">
      <svg className="w-full h-full transform -rotate-90 drop-shadow-sm" viewBox="0 0 36 36">
        <path
          className="text-muted/20"
          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
        />
        <motion.path
          className={color}
          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeDasharray={`${percentage}, 100`}
          initial={{ strokeDasharray: "0, 100" }}
          animate={{ strokeDasharray: `${percentage}, 100` }}
          transition={{ duration: 1.5, ease: "easeOut", delay: 0.2 }}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span 
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="text-3xl font-black tracking-tighter"
        >
          {score.toFixed(1)}
        </motion.span>
        <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest mt-0.5">CVSS</span>
      </div>
    </div>
  );
};

const getSeverityStyles = (severity: string) => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return {
        bg: 'bg-red-500/10',
        border: 'border-red-500/30',
        text: 'text-red-600 dark:text-red-400',
        shadow: 'shadow-red-500/10',
        icon: 'text-red-500',
        solid: 'bg-red-500'
      };
    case 'high':
      return {
        bg: 'bg-orange-500/10',
        border: 'border-orange-500/30',
        text: 'text-orange-600 dark:text-orange-400',
        shadow: 'shadow-orange-500/10',
        icon: 'text-orange-500',
        solid: 'bg-orange-500'
      };
    case 'medium':
      return {
        bg: 'bg-yellow-500/10',
        border: 'border-yellow-500/30',
        text: 'text-yellow-600 dark:text-yellow-400',
        shadow: 'shadow-yellow-500/10',
        icon: 'text-yellow-500',
        solid: 'bg-yellow-500'
      };
    case 'low':
      return {
        bg: 'bg-green-500/10',
        border: 'border-green-500/30',
        text: 'text-green-600 dark:text-green-400',
        shadow: 'shadow-green-500/10',
        icon: 'text-green-500',
        solid: 'bg-green-500'
      };
    default:
      return {
        bg: 'bg-muted/50',
        border: 'border-border',
        text: 'text-muted-foreground',
        shadow: 'shadow-none',
        icon: 'text-muted-foreground',
        solid: 'bg-muted-foreground'
      };
  }
};

export default function VulnerabilitiesPage() {
  const [cveId, setCveId] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [result, setResult] = useState<VulnerabilityData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    const trimmedId = cveId.trim().toUpperCase();
    if (!trimmedId) return;

    // Basic format validation: CVE-YYYY-NNNNN
    if (!/^CVE-\d{4}-\d{4,}$/.test(trimmedId)) {
      setError('Invalid CVE format. Expected format: CVE-YYYY-NNNNN');
      setResult(null);
      return;
    }

    setIsSearching(true);
    setError(null);
    setResult(null);
    try {
      const response = await ctiApi.getVulnerability(trimmedId);
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch vulnerability data.');
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto pb-12">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center gap-4"
      >
        <div className="p-3 bg-primary/10 rounded-xl">
          <Shield className="h-8 w-8 text-primary" />
        </div>
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Vulnerability Intelligence</h1>
          <p className="text-muted-foreground mt-1 text-lg">
            Retrieve detailed threat intelligence, CVSS scoring, and mitigations.
          </p>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Card className="border-2 shadow-sm hover:shadow-md transition-shadow duration-300">
          <CardHeader className="pb-4">
            <CardTitle className="text-xl">CVE Database Query</CardTitle>
            <CardDescription className="text-base">Enter a valid CVE identifier (e.g., CVE-2024-12345) to scan the database.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1 group">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                <Input
                  placeholder="CVE-2024-..."
                  className="pl-12 h-14 text-lg bg-muted/20 border-muted-foreground/20 focus-visible:ring-primary focus-visible:border-primary transition-all rounded-xl shadow-inner"
                  value={cveId}
                  onChange={(e) => setCveId(e.target.value.toUpperCase())}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSearch();
                  }}
                  disabled={isSearching}
                />
                <div className="absolute inset-0 rounded-xl ring-1 ring-inset ring-primary/20 opacity-0 group-focus-within:opacity-100 transition-opacity pointer-events-none" />
              </div>
              <Button 
                onClick={handleSearch} 
                disabled={isSearching || !cveId.trim()} 
                className="h-14 px-8 text-base font-semibold rounded-xl"
              >
                {isSearching ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : 'Scan Database'}
              </Button>
            </div>

            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <Alert variant="destructive" className="mt-4 border-red-500/30 bg-red-500/10 text-red-600 dark:text-red-400">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="ml-2 font-medium">{error}</AlertDescription>
                  </Alert>
                </motion.div>
              )}
            </AnimatePresence>
          </CardContent>
        </Card>
      </motion.div>

      <AnimatePresence mode="wait">
        {isSearching && (
          <motion.div
            key="loading"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="relative overflow-hidden border-2 rounded-2xl bg-card p-12 flex flex-col items-center justify-center shadow-sm"
          >
            <motion.div
              animate={{ 
                y: ["-100%", "300%"],
                opacity: [0, 1, 1, 0]
              }}
              transition={{ 
                repeat: Infinity, 
                duration: 2.5,
                ease: "linear"
              }}
              className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-transparent via-primary/10 to-transparent w-full z-0 pointer-events-none"
            />
            <div className="relative z-10 flex flex-col items-center gap-6 text-center">
              <div className="relative flex items-center justify-center h-20 w-20">
                <Activity className="h-10 w-10 text-primary z-10" />
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
              </div>
              <div>
                <h3 className="text-xl font-bold text-primary mb-2">Querying Threat Databases...</h3>
                <p className="text-muted-foreground">Retrieving severity metrics, descriptions, and mitigation strategies</p>
              </div>
            </div>
          </motion.div>
        )}

        {!isSearching && !result && !error && (
          <motion.div 
            key="empty"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center py-20 px-4 text-center border-2 border-dashed rounded-2xl bg-muted/5"
          >
            <div className="bg-muted p-5 rounded-full mb-6">
              <Fingerprint className="h-10 w-10 text-muted-foreground" />
            </div>
            <h3 className="text-2xl font-bold mb-3 text-foreground/80">Awaiting Search Query</h3>
            <p className="text-muted-foreground max-w-md text-lg">
              Enter a vulnerability identifier above to retrieve comprehensive threat intelligence.
            </p>
          </motion.div>
        )}

        {result && !isSearching && (() => {
          const styles = getSeverityStyles(result.severity);
          return (
            <motion.div
              key="result"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ type: "spring" as const, stiffness: 100, damping: 20 }}
              className={`overflow-hidden rounded-2xl border-2 ${styles.border} shadow-lg ${styles.shadow} bg-card relative`}
            >
              <div className={`absolute top-0 left-0 w-full h-1.5 ${styles.solid}`} />
              
              <div className="p-8 sm:p-10">
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-8 mb-10 border-b pb-8">
                  <div className="space-y-4 max-w-2xl">
                    <div className="flex items-center gap-4 flex-wrap">
                      <div className={`p-3 rounded-xl ${styles.bg}`}>
                        <Bug className={`h-8 w-8 ${styles.icon}`} />
                      </div>
                      <h2 className="text-4xl font-extrabold tracking-tight">{result.id}</h2>
                      <Badge variant="outline" className={`${styles.bg} ${styles.text} ${styles.border} uppercase px-4 py-1.5 text-sm font-bold tracking-widest rounded-lg`}>
                        {result.severity} Severity
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="flex-shrink-0 bg-background/50 p-4 rounded-2xl border shadow-inner">
                    <CVSSGauge score={result.cvss_score} />
                  </div>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                  <section className="lg:col-span-2 space-y-4">
                    <h3 className="text-sm font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
                      <Activity className="h-4 w-4" />
                      Vulnerability Description
                    </h3>
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <p className="text-lg leading-relaxed text-foreground/90">
                        {result.description}
                      </p>
                    </div>
                  </section>
                  
                  <section className="space-y-4 lg:col-span-1">
                    <h3 className="text-sm font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
                      <ShieldAlert className="h-4 w-4" />
                      Remediation
                    </h3>
                    {result.mitigation ? (
                      <motion.div 
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 }}
                        className="bg-muted/30 border rounded-xl p-5 text-sm leading-relaxed whitespace-pre-wrap font-mono relative overflow-hidden group hover:bg-muted/50 transition-colors"
                      >
                        <div className={`absolute top-0 left-0 w-1.5 h-full ${styles.solid} opacity-70`} />
                        <span className="relative z-10">{result.mitigation}</span>
                      </motion.div>
                    ) : (
                      <div className="bg-muted/10 border border-dashed rounded-xl p-5 text-sm text-muted-foreground flex items-start gap-3">
                        <AlertCircle className="h-5 w-5 opacity-50 shrink-0 mt-0.5" />
                        <p className="leading-relaxed">No explicit mitigation steps are currently documented. Ensure systems are patched to the latest vendor releases.</p>
                      </div>
                    )}
                  </section>
                </div>
              </div>
            </motion.div>
          );
        })()}
      </AnimatePresence>
    </div>
  );
}
