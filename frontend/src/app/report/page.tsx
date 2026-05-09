'use client';

import { useState } from 'react';
import { FileText, Download, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { ctiApi } from '@/services/api';

export default function ReportPage() {
  const [formData, setFormData] = useState({
    query: '',
    query_response: '',
    classification: 'Unknown',
    classification_confidence: 0,
    risk_score: 0,
    risk_label: 'Low',
  });
  
  const [vulnInput, setVulnInput] = useState(''); // Simple comma separated IDs for demo
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'classification_confidence' || name === 'risk_score' ? Number(value) : value,
    }));
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setStatus('idle');
    setErrorMessage('');

    // Process vulnerabilities
    const vulnerabilities = vulnInput
      .split(',')
      .map(id => id.trim())
      .filter(id => id.length > 0)
      .map(id => ({
        id,
        severity: 'High', // Defaulting for manual entry
        description: `Manual entry for ${id}`,
      }));

    const payload = {
      ...formData,
      vulnerabilities,
    };

    try {
      const blob = await ctiApi.generateReport(payload);
      
      if (!blob || !(blob instanceof Blob)) {
        throw new Error('Invalid response from server.');
      }

      // Create a URL for the blob and trigger download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'CTI_Analysis_Report.pdf');
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      setStatus('success');
    } catch (error: any) {
      console.error(error);
      setStatus('error');
      setErrorMessage(error.message || 'An error occurred while generating the report.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-4xl mx-auto">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Report Generator</h1>
        <p className="text-muted-foreground">
          Compile your analytical findings and export them as a structured PDF document.
        </p>
      </div>

      <Card className="border-2 shadow-sm">
        <CardHeader className="bg-muted/20 border-b pb-6">
          <div className="flex items-center gap-2 mb-2">
            <FileText className="h-6 w-6 text-primary" />
            <CardTitle>Report Details</CardTitle>
          </div>
          <CardDescription>
            Fill in the sections below. This data will be compiled and formatted into the final PDF.
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6 pt-6">
          {status === 'success' && (
            <Alert className="bg-emerald-500/15 text-emerald-500 border-emerald-500/30">
              <CheckCircle2 className="h-4 w-4" />
              <AlertTitle>Success</AlertTitle>
              <AlertDescription>
                Your PDF report has been generated and downloaded successfully.
              </AlertDescription>
            </Alert>
          )}

          {status === 'error' && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Generation Failed</AlertTitle>
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}

          <div className="grid gap-6 md:grid-cols-2">
            {/* Query Section */}
            <div className="space-y-4 md:col-span-2">
              <h3 className="text-lg font-semibold border-b pb-2">1. Query Analysis</h3>
              <div className="space-y-2">
                <Label htmlFor="query">Analyst Query</Label>
                <Input 
                  id="query" 
                  name="query" 
                  placeholder="e.g., What are the latest IOCs for APT29?" 
                  value={formData.query}
                  onChange={handleChange}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="query_response">AI Response / Finding</Label>
                <Textarea 
                  id="query_response" 
                  name="query_response" 
                  placeholder="Enter the analytical response here..." 
                  className="min-h-[120px]"
                  value={formData.query_response}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Classification Section */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold border-b pb-2">2. Threat Classification</h3>
              <div className="space-y-2">
                <Label htmlFor="classification">Category</Label>
                <Input 
                  id="classification" 
                  name="classification" 
                  placeholder="e.g., Malware, Phishing" 
                  value={formData.classification}
                  onChange={handleChange}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="classification_confidence">Confidence Score (0.0 - 1.0)</Label>
                <Input 
                  id="classification_confidence" 
                  name="classification_confidence" 
                  type="number" 
                  step="0.01" 
                  min="0" 
                  max="1"
                  value={formData.classification_confidence}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Risk Section */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold border-b pb-2">3. Risk Assessment</h3>
              <div className="space-y-2">
                <Label htmlFor="risk_score">Overall Risk Score (0 - 100)</Label>
                <Input 
                  id="risk_score" 
                  name="risk_score" 
                  type="number" 
                  min="0" 
                  max="100"
                  value={formData.risk_score}
                  onChange={handleChange}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="risk_label">Risk Label</Label>
                <Input 
                  id="risk_label" 
                  name="risk_label" 
                  placeholder="e.g., Critical, High, Medium, Low" 
                  value={formData.risk_label}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Vulnerability Section */}
            <div className="space-y-4 md:col-span-2">
              <h3 className="text-lg font-semibold border-b pb-2">4. Vulnerabilities</h3>
              <div className="space-y-2">
                <Label htmlFor="vulnInput">Associated CVEs (comma separated)</Label>
                <Input 
                  id="vulnInput" 
                  placeholder="e.g., CVE-2023-1234, CVE-2024-5678" 
                  value={vulnInput}
                  onChange={(e) => setVulnInput(e.target.value)}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Enter CVE IDs to include them in the vulnerability analysis section.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
        
        <CardFooter className="bg-muted/20 border-t p-6 flex justify-end">
          <Button 
            onClick={handleGenerate} 
            disabled={isGenerating}
            size="lg"
            className="w-full md:w-auto gap-2"
          >
            {isGenerating ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Generating PDF...
              </>
            ) : (
              <>
                <Download className="h-5 w-5" />
                Download PDF Report
              </>
            )}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
