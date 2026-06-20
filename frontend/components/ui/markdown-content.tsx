"use client"

import React from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeRaw from "rehype-raw"
import { Code, AlertTriangle, Info, AlertCircle, Lightbulb } from "lucide-react"
import dynamic from "next/dynamic"

const CodeBlock = dynamic(() => import("@/components/ui/code-block").then(m => ({ default: m.CodeBlock })), { ssr: false })

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
