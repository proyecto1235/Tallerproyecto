"use client"

import dynamic from "next/dynamic"

const ChatWidgetInner = dynamic(
  () => import("@/components/chat/chat-widget").then((m) => ({ default: m.ChatWidget })),
  { ssr: false },
)

export function ChatWidgetLazy() {
  return <ChatWidgetInner />
}
