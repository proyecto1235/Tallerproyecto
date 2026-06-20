import type { Metadata } from 'next'
import { Analytics } from '@vercel/analytics/next'
import { Inter, Orbitron } from 'next/font/google'
import { ThemeProvider } from '@/components/theme-provider'
import { Toaster } from 'sonner'
import { ErrorBoundary } from '@/components/error-boundary'
import { ChatWidgetLazy } from '@/components/chat/chat-widget-lazy'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const orbitron = Orbitron({ subsets: ['latin'], variable: '--font-orbitron' })

export const metadata: Metadata = {
  title: 'RoboLearn - Aprende Programación y Robótica',
  description: 'Plataforma educativa de programación y robótica para estudiantes. Aprende Python de forma divertida con ejercicios interactivos, retos y gamificación.',
  generator: 'v0.app',
  icons: {
    icon: [
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/icon.svg',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es" suppressHydrationWarning className={`${inter.variable} ${orbitron.variable}`}>
      <body className="font-sans antialiased min-h-screen bg-background text-foreground">
        <ThemeProvider>
          {children}
          <div className="crt-scanlines crt-flicker" />
          <div className="crt-vignette" />
          <ChatWidgetLazy />
          <Toaster
            position="bottom-right"
            richColors
            closeButton
            duration={10000}
            visibleToasts={5}
          />
          {process.env.NODE_ENV === 'production' && <Analytics />}
        </ThemeProvider>
      </body>
    </html>
  )
}
