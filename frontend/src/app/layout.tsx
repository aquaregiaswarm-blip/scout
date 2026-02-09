import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Scout | Sales Intelligence",
  description: "Agentic sales intelligence for VAR/SI teams",
  icons: {
    icon: '/icon',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <aside className="w-64 border-r border-white/10 p-6 hidden md:block">
            <div className="flex items-center gap-3 mb-8">
              <span className="text-3xl">🔭</span>
              <div>
                <h1 className="text-xl font-bold text-white">Scout</h1>
                <p className="text-xs text-gray-500">Sales Intelligence</p>
              </div>
            </div>
            <nav className="space-y-2">
              <a href="/" className="block px-4 py-2 rounded-lg hover:bg-white/5 text-gray-300 hover:text-white transition-colors">
                New Research
              </a>
              <a href="/companies" className="block px-4 py-2 rounded-lg hover:bg-white/5 text-gray-300 hover:text-white transition-colors">
                Companies
              </a>
              <a href="/portfolio" className="block px-4 py-2 rounded-lg hover:bg-white/5 text-gray-300 hover:text-white transition-colors">
                Portfolio
              </a>
            </nav>
          </aside>
          
          {/* Main content */}
          <main className="flex-1 p-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
