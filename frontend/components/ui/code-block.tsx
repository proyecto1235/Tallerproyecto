"use client"

import { useState } from "react"
import { Copy, Check } from "lucide-react"
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism"

export function CodeBlock({ className, children }: { className?: string; children: React.ReactNode }) {
  const [copied, setCopied] = useState(false)
  const match = /language-(\w+)/.exec(className || "")
  const language = match ? match[1] : ""
  const code = String(children).replace(/\n$/, "")

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  try {
    return (
      <div className="relative group my-4 rounded-xl overflow-hidden border border-border">
        <div className="flex items-center justify-between bg-muted/80 px-4 py-2 border-b border-border">
          <span className="text-xs font-mono text-muted-foreground uppercase">{language || "code"}</span>
          <button onClick={handleCopy} className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors">
            {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? "Copiado" : "Copiar"}
          </button>
        </div>
        <SyntaxHighlighter
          style={oneDark}
          language={language || "python"}
          PreTag="div"
          customStyle={{ margin: 0, borderRadius: 0, fontSize: "0.875rem" }}
          showLineNumbers
        >
          {code}
        </SyntaxHighlighter>
      </div>
    )
  } catch {
    return (
      <pre className="relative group my-4 rounded-xl overflow-hidden border border-border bg-muted p-4 overflow-x-auto">
        <button onClick={handleCopy} className="absolute top-2 right-2 p-1.5 rounded-lg bg-background/50 opacity-0 group-hover:opacity-100 transition-opacity">
          {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
        </button>
        <code className={`text-sm font-mono ${className}`}>{children}</code>
      </pre>
    )
  }
}
