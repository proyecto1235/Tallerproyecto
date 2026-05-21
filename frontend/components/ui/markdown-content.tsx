"use client"

import React from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeRaw from "rehype-raw"
import { Code, Copy, Check, AlertTriangle, Info, AlertCircle, Lightbulb } from "lucide-react"
import { useState } from "react"
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism"

const isServer = typeof window === "undefined"

function CodeBlock({ className, children }: { className?: string; children: React.ReactNode }) {
  const [copied, setCopied] = useState(false)
  const match = /language-(\w+)/.exec(className || "")
  const language = match ? match[1] : ""
  const code = String(children).replace(/\n$/, "")

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (!isServer) {
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
    } catch { }
  }

  return (
    <pre className="relative group my-4 rounded-xl overflow-hidden border border-border bg-muted p-4 overflow-x-auto">
      <button onClick={handleCopy} className="absolute top-2 right-2 p-1.5 rounded-lg bg-background/50 opacity-0 group-hover:opacity-100 transition-opacity">
        {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
      </button>
      <code className={`text-sm font-mono ${className}`}>{children}</code>
    </pre>
  )
}

function AlertBlock({ children, type }: { children: React.ReactNode; type: string }) {
  const config: Record<string, { icon: React.ReactNode; color: string; bg: string; border: string; label: string }> = {
    important: {
      icon: <AlertTriangle className="w-5 h-5" />,
      color: "text-amber-500", bg: "bg-amber-500/5", border: "border-amber-500/20", label: "Importante"
    },
    warning: {
      icon: <AlertTriangle className="w-5 h-5" />,
      color: "text-orange-500", bg: "bg-orange-500/5", border: "border-orange-500/20", label: "Advertencia"
    },
    info: {
      icon: <Info className="w-5 h-5" />,
      color: "text-blue-500", bg: "bg-blue-500/5", border: "border-blue-500/20", label: "Información"
    },
    tip: {
      icon: <Lightbulb className="w-5 h-5" />,
      color: "text-emerald-500", bg: "bg-emerald-500/5", border: "border-emerald-500/20", label: "Consejo"
    },
    danger: {
      icon: <AlertCircle className="w-5 h-5" />,
      color: "text-red-500", bg: "bg-red-500/5", border: "border-red-500/20", label: "Peligro"
    },
  }

  const c = config[type] || config.info

  return (
    <div className={`${c.bg} ${c.border} border rounded-xl p-4 my-4`}>
      <div className="flex items-start gap-3">
        <div className={`mt-0.5 ${c.color}`}>{c.icon}</div>
        <div className="flex-1">
          <p className={`text-xs font-bold uppercase tracking-wider ${c.color} mb-1`}>{c.label}</p>
          <div className="text-sm text-foreground/90 prose prose-invert max-w-none">{children}</div>
        </div>
      </div>
    </div>
  )
}

function processAlertBlock(children: React.ReactNode): React.ReactNode {
  const text = extractText(children)
  const match = text.match(/^\[!(IMPORTANT|WARNING|INFO|TIP|DANGER)\]/i)
  if (match) {
    const type = match[1].toLowerCase()
    const rest = removeFirstLine(text)
    return <AlertBlock type={type}>{rest}</AlertBlock>
  }
  return <blockquote className="border-l-4 border-primary/30 pl-4 my-4 italic text-muted-foreground">{children}</blockquote>
}

function extractText(node: React.ReactNode): string {
  if (typeof node === "string") return node
  if (Array.isArray(node)) return node.map(extractText).join("")
  if (node && typeof node === "object" && "props" in node) {
    return extractText((node as any).props.children)
  }
  return ""
}

function removeFirstLine(text: string): string {
  const lines = text.split("\n")
  lines.shift()
  return lines.join("\n").trim()
}

export function MarkdownContent({ content, className = "" }: { content: string; className?: string }) {
  return (
    <div className={`prose prose-invert max-w-none ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
        components={{
          code({ className, children, ...props }) {
            const isInline = !className
            if (isInline) {
              return <code className="bg-muted px-1.5 py-0.5 rounded-md text-sm font-mono text-primary" {...props}>{children}</code>
            }
            return <code className={className} {...props}>{children}</code>
          },
          pre({ children }) {
            const codeNode = (children as any)?.props
            const className = codeNode?.className || ""
            const code = codeNode?.children || ""
            return <CodeBlock className={className}>{code}</CodeBlock>
          },
          blockquote({ children }) {
            return processAlertBlock(children)
          },
          table({ children }) {
            return (
              <div className="overflow-x-auto my-4 rounded-xl border border-border">
                <table className="min-w-full divide-y divide-border text-sm">{children}</table>
              </div>
            )
          },
          th({ children }) {
            return <th className="px-4 py-3 bg-muted/50 font-semibold text-left">{children}</th>
          },
          td({ children }) {
            return <td className="px-4 py-3 border-t border-border">{children}</td>
          },
          a({ href, children }) {
            return <a href={href} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">{children}</a>
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
