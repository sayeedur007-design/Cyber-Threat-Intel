import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/navbar";
import { Sidebar } from "@/components/sidebar";
import { AuthProvider } from "@/components/AuthProvider";
import { PageTransition } from "@/components/page-transition";

export const metadata: Metadata = {
  title: "CTI Analyst Platform",
  description: "Cyber Threat Intelligence Dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className="dark"
      suppressHydrationWarning
    >
      <body className="min-h-screen bg-background font-sans antialiased">
        <AuthProvider>
          <Navbar />
          <div className="flex min-h-[calc(100vh-4rem)]">
            <Sidebar />
            <main className="flex-1 p-8 bg-muted/20 overflow-x-hidden flex flex-col">
              <PageTransition>
                {children}
              </PageTransition>
            </main>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
