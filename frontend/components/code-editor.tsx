"use client"

import dynamic from "next/dynamic"

const CodeMirror = dynamic(() => import("@uiw/react-codemirror"), { ssr: false })

export function CodeEditor(props: any) {
  return <CodeMirror {...props} />
}
