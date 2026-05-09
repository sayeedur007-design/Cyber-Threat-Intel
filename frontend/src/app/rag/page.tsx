'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Send, Bot, User, Loader2, AlertCircle, Database, Upload } from 'lucide-react';
import { ctiApi } from '@/services/api';


interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  confidenceScore?: number;
  sources?: string[];
  isError?: boolean;
}

export default function RagInterfacePage() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, isUploading]);

  const handleSubmit = async () => {
    if (!query.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: query.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    try {
      const response = await ctiApi.ragQuery(userMessage.content);
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer || response.response || 'No response provided.',
        confidenceScore: response.confidenceScore || response.confidence_score,
        sources: response.sources,
        isError: !!response.error,
      };

      if (response.error) {
        assistantMessage.content = response.error;
      }

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      let errorMsg = 'An unexpected error occurred.';
      if (error.code === 'ECONNABORTED') {
        errorMsg = 'API request timed out. The backend took too long to respond.';
      } else if (error.response?.data?.detail) {
        errorMsg = error.response.data.detail;
      } else if (error.message) {
        errorMsg = error.message;
      }

      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: errorMsg,
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    
    setIsUploading(true);
    const files = Array.from(e.target.files);
    
    try {
      const response = await ctiApi.indexDocuments(files);
      
      const systemMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `✅ Successfully indexed ${files.length} document(s). ${response.message || ''} (${response.chunks || 0} chunks added.)`,
      };
      setMessages((prev) => [...prev, systemMessage]);
    } catch (error: any) {
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `❌ Upload failed: ${error.message || 'Unknown error'}`,
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
  <div className="h-full flex flex-col">

    <Card className="flex-1 flex flex-col overflow-hidden border-border/50 bg-card/30 backdrop-blur-md shadow-2xl rounded-2xl ring-1 ring-white/5">
      
      <CardHeader className="flex flex-row items-center justify-between border-b border-border/40 bg-white/[0.02] py-4">
        <div className="flex items-center gap-4">
          <div className="p-2.5 bg-primary/10 rounded-xl border border-primary/20 shadow-[0_0_15px_rgba(0,255,198,0.1)]">
            <Database className="w-5 h-5 text-primary" />
          </div>
          <div>
            <CardTitle className="text-lg font-black tracking-tight text-slate-100 uppercase">
              Intelligence <span className="text-primary">Navigator</span>
            </CardTitle>
            <CardDescription className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/80 flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Strategic RAG Engine Active
            </CardDescription>
          </div>
        </div>

        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="h-9 border-border/60 hover:border-primary/40 hover:bg-primary/5 transition-all rounded-lg"
          >
            {isUploading ? <Loader2 className="w-4 h-4 animate-spin text-primary"/> : <Upload className="w-4 h-4 mr-2"/>}
            <span className="text-xs font-bold uppercase tracking-wider">Ingest Docs</span>
          </Button>

          <input
            type="file"
            multiple
            ref={fileInputRef}
            className="hidden"
            onChange={handleFileUpload}
          />
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">

        <ScrollArea className="h-[calc(100vh-12rem)]">
          <div className="space-y-4 max-w-4xl mx-auto p-4">

            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
                <div className="p-4 bg-primary/5 rounded-full border border-primary/10">
                  <Bot className="w-10 h-10 text-primary opacity-50" />
                </div>
                <div className="space-y-1">
                  <p className="text-slate-200 font-bold">Strategic Intelligence Ready</p>
                  <p className="text-muted-foreground text-xs max-w-xs leading-relaxed">
                    Query APT activity, Kill Chains, ATT&CK techniques, SIEM detections, or infrastructure overlaps.
                  </p>
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0 mt-1">
                      <Bot className="w-4 h-4 text-primary" />
                    </div>
                  )}

                  <div className={`max-w-[85%] rounded-2xl p-4 shadow-sm relative group ${
                    msg.role === 'user' 
                      ? "bg-primary/10 border border-primary/20 text-slate-100 rounded-tr-none" 
                      : msg.isError 
                        ? "bg-destructive/10 border border-destructive/20 text-destructive rounded-tl-none" 
                        : "bg-card border border-border/50 text-slate-200 rounded-tl-none"
                  }`}>
                    {msg.role === 'assistant' ? (
                      <div className="prose prose-sm dark:prose-invert max-w-none text-slate-200 leading-relaxed space-y-2 whitespace-pre-wrap">
                        {msg.content}
                      </div>
                    ) : (
                      <p className="text-sm font-medium leading-relaxed">{msg.content}</p>
                    )}

                    {msg.confidenceScore !== undefined && (
                      <div className="mt-4 pt-3 border-t border-border/40 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="h-1 w-20 bg-muted rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-primary" 
                              style={{ width: `${Math.round(msg.confidenceScore * 100)}%` }} 
                            />
                          </div>
                          <span className="text-[10px] font-black uppercase tracking-wider text-muted-foreground">
                            {Math.round(msg.confidenceScore * 100)}% Confidence
                          </span>
                        </div>
                        {msg.sources && msg.sources.length > 0 && (
                          <span className="text-[10px] font-bold text-primary/70 hover:text-primary cursor-pointer transition-colors">
                            {msg.sources.length} SOURCES
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center shrink-0 mt-1">
                      <User className="w-4 h-4 text-slate-400" />
                    </div>
                  )}
                </div>
              ))
            )}

            <div ref={messagesEndRef}/>
          </div>
        </ScrollArea>

        <div className="p-6 border-t border-border/40 bg-white/[0.01]">
          <div className="max-w-4xl mx-auto relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-primary/20 to-transparent rounded-2xl blur opacity-0 group-focus-within:opacity-100 transition duration-500" />
            <div className="relative flex gap-3 bg-card/60 backdrop-blur-xl border border-border/60 p-2 rounded-2xl shadow-xl focus-within:border-primary/50 transition-all">
              <Textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Query threat intelligence knowledge base..."
                className="flex-1 min-h-[56px] max-h-32 bg-transparent border-0 focus-visible:ring-0 resize-none text-sm py-3 px-2 text-slate-100 placeholder:text-muted-foreground/60"
              />

              <Button 
                onClick={handleSubmit} 
                disabled={isLoading || !query.trim()}
                className={`h-auto px-4 rounded-xl transition-all duration-300 ${
                  query.trim() 
                    ? "bg-primary text-primary-foreground shadow-[0_0_15px_rgba(0,255,198,0.3)] hover:scale-105" 
                    : "bg-muted text-muted-foreground opacity-50"
                }`}
              >
                {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
              </Button>
            </div>
          </div>
        </div>

      </CardContent>
    </Card>

  </div>
)

  
   
}
