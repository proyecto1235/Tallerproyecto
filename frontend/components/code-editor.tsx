"use client"

import dynamic from "next/dynamic"
import type { ReactCodeMirrorProps } from "@uiw/react-codemirror"

const CodeMirror = dynamic(() => import("@uiw/react-codemirror"), { ssr: false })

export function CodeEditor(props: ReactCodeMirrorProps) {
  return <CodeMirror {...props} />
}
