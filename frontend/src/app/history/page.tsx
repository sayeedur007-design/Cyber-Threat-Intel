'use client';

import { useState, useEffect, useMemo } from 'react';
import { Trash2, History as HistoryIcon, Search, ChevronDown, Clock, ShieldAlert, Activity, ShieldCheck, Fingerprint, Calendar } from 'lucide-react';
import { format } from 'date-fns';
import { motion, AnimatePresence } from 'framer-motion';

import { ctiApi } from '@/services/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Loader } from '@/components/loader';

interface HistoryEntry {
  id: number;
  query: string;
  response: string;
  timestamp: string;
}

// Pseudo-metadata inference to enhance visual presentation of the timeline
const inferMetadata = (query: string, response: string) => {
  const text = (query + " " + response).toLowerCase();
  let severity = 'Low';
  if (text.includes('critical') || text.includes('cve-') || text.includes('exploit') || text.includes('breach') || text.includes('apt')) {
    severity = 'Critical';
  } else if (text.includes('high') || text.includes('vulnerability') || text.includes('malware') || text.includes('attack')) {
    severity = 'High';
  } else if (text.includes('medium') || text.includes('suspicious') || text.includes('risk')) {
    severity = 'Medium';
  }

  const tags = [];
  if (text.includes('cve')) tags.push('CVE Lookup');
  if (text.includes('ip ') || text.match(/\d{1,3}\.\d{1,3}/)) tags.push('IP Analysis');
  if (text.includes('domain') || text.includes('url')) tags.push('Domain Intel');
  if (text.includes('malware') || text.includes('ransomware')) tags.push('Malware');
  if (text.includes('actor') || text.includes('apt')) tags.push('Threat Actor');
  
  if (tags.length === 0) tags.push('Threat Analysis');

  return { severity, tags: tags.slice(0, 3) };
};

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'Critical': return 'bg-red-500/10 text-red-400 border-red-500/30';
    case 'High': return 'bg-orange-500/10 text-orange-400 border-orange-500/30';
    case 'Medium': return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30';
    case 'Low': return 'bg-green-500/10 text-green-400 border-green-500/30';
    default: return 'bg-muted text-muted-foreground border-border';
  }
};

const getSeverityIcon = (severity: string) => {
  switch (severity) {
    case 'Critical': return <ShieldAlert className="h-3 w-3 mr-1.5" />;
    case 'High': return <Activity className="h-3 w-3 mr-1.5" />;
    case 'Medium': return <ShieldAlert className="h-3 w-3 mr-1.5 opacity-80" />;
    case 'Low': return <ShieldCheck className="h-3 w-3 mr-1.5" />;
    default: return null;
  }
};

const TimelineItem = ({ entry, onDelete }: { entry: HistoryEntry, onDelete: (id: number) => void }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const metadata = useMemo(() => inferMetadata(entry.query, entry.response), [entry.query, entry.response]);

  return (
    <motion.div 
      layout
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="relative pl-8 md:pl-0"
    >
      {/* Timeline connector */}
      <div className="absolute left-[7.5rem] top-8 bottom-[-2rem] w-[2px] bg-gradient-to-b from-primary/30 via-border/40 to-transparent z-0 last:hidden hidden md:block" />
      
      <div className="flex flex-col md:flex-row gap-6 group relative z-10 pb-10">
        {/* Timestamp sidebar */}
        <div className="md:w-28 shrink-0 pt-4 text-left md:text-right flex md:flex-col items-center md:items-end gap-3 relative">
          <div className="hidden md:flex absolute left-[7.5rem] top-5 w-4 h-4 rounded-full bg-background border-2 border-primary/40 translate-x-[-7px] z-10 group-hover:scale-125 group-hover:border-primary group-hover:shadow-[0_0_10px_rgba(0,255,198,0.4)] transition-all duration-300" />
          <span className="text-sm font-black text-slate-100 tracking-tight flex items-center gap-1.5">
            {format(new Date(entry.timestamp), 'MMM d')}
          </span>
          <span className="text-[10px] text-muted-foreground font-mono flex items-center gap-1.5 px-2 py-0.5 rounded-md border border-border/50 bg-white/5">
            <Clock className="h-3 w-3" />
            {format(new Date(entry.timestamp), 'HH:mm')}
          </span>
        </div>

        {/* Content Card */}
        <Card 
          className={`flex-1 border transition-all duration-500 cursor-pointer ${isExpanded ? 'border-primary/50 shadow-2xl bg-card ring-1 ring-primary/20' : 'border-border/40 hover:border-primary/40 bg-card/80 hover:bg-card'} overflow-hidden rounded-2xl group/item`}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="p-6">
            <div className="flex items-start justify-between gap-6">
              <div className="space-y-4 flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant="outline" className={`px-2 py-0.5 text-[9px] uppercase font-black tracking-widest rounded-lg border ${getSeverityColor(metadata.severity)}`}>
                    {getSeverityIcon(metadata.severity)}
                    {metadata.severity}
                  </Badge>
                  {metadata.tags.map(tag => (
                    <Badge key={tag} variant="secondary" className="px-2 py-0.5 text-[9px] rounded-lg font-bold text-slate-400 bg-white/5 border-transparent hover:bg-white/10 transition-colors">
                      {tag}
                    </Badge>
                  ))}
                </div>
                
                <h3 className="font-bold text-lg md:text-xl text-slate-50 leading-snug group-hover/item:text-primary transition-colors duration-300">
                  {entry.query}
                </h3>
              </div>

              <div className="flex items-center gap-3 shrink-0 pt-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="opacity-0 group-hover:opacity-100 transition-all duration-300 text-destructive/70 hover:bg-destructive/10 hover:text-destructive h-8 w-8 rounded-full"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(entry.id);
                  }}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
                <div className={`p-1.5 rounded-lg border border-border/50 transition-all duration-500 ${isExpanded ? 'rotate-180 bg-primary/10 border-primary/30 text-primary' : 'group-hover:border-primary/30 group-hover:text-primary'}`}>
                  <ChevronDown className="h-4 w-4" />
                </div>
              </div>
            </div>

            <AnimatePresence>
              {isExpanded ? (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
                >
                  <div className="mt-6 pt-6 border-t border-border/50">
                    <div className="flex items-center gap-2 mb-4">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                      <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground">
                        Tactical Analysis Response
                      </h4>
                    </div>
                    <div className="relative group/code">
                      <div className="absolute -inset-1 bg-gradient-to-r from-primary/10 to-transparent rounded-2xl blur opacity-0 group-hover/code:opacity-100 transition duration-1000" />
                      <div className="relative prose prose-sm dark:prose-invert max-w-none bg-black/40 p-6 rounded-xl border border-white/10 text-slate-200 leading-relaxed font-mono text-[13px] whitespace-pre-wrap shadow-inner">
                        <div className="absolute left-0 top-0 bottom-0 w-[3px] bg-primary/50 rounded-l-xl" />
                        {entry.response}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <div className="mt-4 text-sm text-slate-400 line-clamp-2 leading-relaxed font-medium">
                  {entry.response}
                </div>
              )}
            </AnimatePresence>
          </div>
        </Card>
      </div>
    </motion.div>
  );
};

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [filteredHistory, setFilteredHistory] = useState<HistoryEntry[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredHistory(history);
    } else {
      const lower = searchQuery.toLowerCase();
      setFilteredHistory(
        history.filter(
          (h) => h.query.toLowerCase().includes(lower) || h.response.toLowerCase().includes(lower)
        )
      );
    }
  }, [searchQuery, history]);

  const fetchHistory = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await ctiApi.getHistory();
      if (data.history) {
        setHistory(data.history);
        setFilteredHistory(data.history);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load history');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await ctiApi.deleteHistory(id);
      setHistory(history.filter((h) => h.id !== id));
    } catch (err: any) {
      alert(err.message || 'Failed to delete entry');
    }
  };

  return (
    <div className="max-w-5xl mx-auto pb-20">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row md:items-center justify-between gap-8 mb-16"
      >
        <div className="flex items-center gap-6">
          <div className="relative">
            <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
            <div className="relative p-4 bg-card border border-primary/20 rounded-2xl shadow-xl">
              <HistoryIcon className="h-8 w-8 text-primary" />
            </div>
          </div>
          <div>
            <h1 className="text-4xl font-black tracking-tighter text-slate-50 uppercase">
              Investigation <span className="text-primary">Timeline</span>
            </h1>
            <p className="text-muted-foreground mt-1 text-sm font-medium flex items-center gap-2">
              <Calendar className="h-3.5 w-3.5" />
              Historical intelligence repository and analysis archive.
            </p>
          </div>
        </div>

        <div className="relative w-full md:w-96 group">
          <div className="absolute inset-0 bg-primary/5 blur opacity-0 group-focus-within:opacity-100 transition-opacity" />
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
          <Input
            type="search"
            placeholder="Search investigation logs..."
            className="pl-11 h-12 bg-card/60 backdrop-blur-sm border border-border/60 focus-visible:ring-1 focus-visible:ring-primary/50 focus-visible:border-primary/50 rounded-xl transition-all shadow-lg text-sm"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </motion.div>

      <div className="relative min-h-[500px]">
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <Loader text="Decrypting intelligence logs..." />
          </div>
        ) : error ? (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }} 
            animate={{ opacity: 1, scale: 1 }} 
            className="flex flex-col items-center justify-center p-12 text-center bg-destructive/5 border border-destructive/20 rounded-3xl"
          >
            <ShieldAlert className="h-12 w-12 text-destructive mb-6 animate-pulse" />
            <h3 className="text-xl font-bold text-slate-50 mb-3">Sync Failure Detected</h3>
            <p className="text-muted-foreground mb-8 max-w-sm">{error}</p>
            <Button onClick={fetchHistory} className="bg-destructive/20 text-destructive border border-destructive/30 hover:bg-destructive/30 rounded-xl px-8">
              Force Sync
            </Button>
          </motion.div>
        ) : filteredHistory.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0, y: 20 }} 
            animate={{ opacity: 1, y: 0 }} 
            className="flex flex-col items-center justify-center py-32 px-4 text-center border border-dashed border-border/60 rounded-3xl bg-white/[0.02]"
          >
            <div className="bg-muted/30 p-6 rounded-2xl mb-8">
              <Fingerprint className="h-12 w-12 text-muted-foreground opacity-40" />
            </div>
            <h3 className="text-2xl font-bold mb-3 text-slate-200">No Intelligence Found</h3>
            <p className="text-muted-foreground text-sm max-w-xs mx-auto leading-relaxed">
              {searchQuery ? "No logs match your search parameters. Try a broader query." : "Your tactical investigation timeline is currently empty."}
            </p>
            {searchQuery && (
              <Button variant="link" onClick={() => setSearchQuery('')} className="mt-6 text-primary hover:text-primary/80">
                Reset Filters
              </Button>
            )}
          </motion.div>
        ) : (
          <div className="space-y-4">
            <AnimatePresence mode="popLayout">
              {filteredHistory.map((entry) => (
                <TimelineItem key={entry.id} entry={entry} onDelete={handleDelete} />
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
}
