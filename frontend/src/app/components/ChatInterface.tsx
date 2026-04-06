"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
  tools_used?: string[];
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/v1/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: userMessage.content }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: "assistant",
        content: data.answer,
        tools_used: data.tools_used,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error fetching response:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again later.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Chat Feed Container */}
      <div className="flex-1 overflow-y-auto custom-scrollbar px-6 py-8 flex flex-col gap-10 max-w-5xl mx-auto w-full pb-48">

        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center opacity-50 mt-20">
            <span className="material-symbols-outlined text-6xl mb-4 text-primary-container">psychology</span>
            <h2 className="text-2xl font-headline font-bold text-on-surface">How can I assist you today?</h2>
            <p className="text-slate-500 max-w-md mt-2 font-body">Ask about market trends, risk reports, or portfolio health using natural language.</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} w-full`}>
              {msg.role === "user" ? (
                <div className="max-w-2xl bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-outline-variant/10">
                  <p className="text-on-surface text-lg leading-relaxed font-medium whitespace-pre-wrap">{msg.content}</p>
                </div>
              ) : (
                <div className="max-w-4xl w-full flex gap-4">
                  <div className="w-10 h-10 rounded bg-primary-container flex items-center justify-center flex-shrink-0">
                    <span className="material-symbols-outlined text-on-primary-container text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>smart_toy</span>
                  </div>
                  <div className="flex flex-col gap-6 w-full">
                    <div className="text-on-surface text-lg leading-relaxed space-y-4">
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    </div>

                    {/* Tool Logs (The "Insight Log") */}
                    {msg.tools_used && msg.tools_used.length > 0 && (
                      <details className="rounded-lg overflow-hidden border border-outline-variant/15 group cursor-pointer bg-primary-container">
                        <summary className="bg-surface-container-low px-4 py-3 flex items-center justify-between list-none">
                          <div className="flex items-center gap-2">
                            <span className="material-symbols-outlined text-sm text-slate-600">terminal</span>
                            <span className="font-body text-xs font-medium uppercase tracking-wider text-slate-600">🛠️ Tool Logs ({msg.tools_used.length})</span>
                          </div>
                          <span className="material-symbols-outlined text-slate-400 text-sm group-open:rotate-180 transition-transform">keyboard_arrow_down</span>
                        </summary>
                        <div className="p-4 font-mono text-[11px] leading-relaxed border-t border-outline-variant/10">
                          {msg.tools_used.map((tool, idx) => (
                            <div key={idx} className={`text-primary-fixed flex items-center gap-2 ${idx > 0 ? 'mt-1' : ''}`}>
                              <span className="opacity-50">T+{idx}</span>
                              <span className="text-on-primary-container font-semibold">{tool}()</span>
                              <span className="text-slate-500 ml-auto">EXECUTED</span>
                            </div>
                          ))}
                        </div>
                      </details>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start w-full animate-pulse">
            <div className="max-w-4xl w-full flex gap-4">
              <div className="w-10 h-10 rounded bg-primary-container flex items-center justify-center flex-shrink-0 opacity-50">
                <span className="material-symbols-outlined text-on-primary-container text-xl">hourglass_empty</span>
              </div>
              <div className="flex flex-col gap-2 w-full mt-2">
                <div className="h-4 bg-surface-container rounded w-3/4"></div>
                <div className="h-4 bg-surface-container rounded w-1/2"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Sticky Bottom Input Area */}
      <div className="fixed bottom-0 right-0 lg:left-64 left-0 p-6 glass-panel z-40">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex flex-col gap-3">
          <div className="relative group">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
              className="w-full bg-surface-container-lowest border border-outline-variant/20 rounded-xl py-4 pl-6 pr-32 focus:outline-none focus:ring-2 ring-on-primary-container/30 text-on-surface placeholder-slate-400 shadow-sm transition-all"
              placeholder="Ask about market trends, risk reports, or portfolio health..."
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
              <button type="button" className="p-2 text-slate-400 hover:text-slate-600 transition-colors hidden sm:block">
                <span className="material-symbols-outlined text-[20px]">attach_file</span>
              </button>
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="bg-primary text-on-primary px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-slate-800 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span className="font-label text-sm font-bold">Send</span>
                <span className="material-symbols-outlined text-sm">send</span>
              </button>
            </div>
          </div>
          <div className="flex items-center justify-between px-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5">
                <span className="material-symbols-outlined text-on-primary-container text-[14px]">lock</span>
                <span className="text-[10px] uppercase font-headline font-bold text-slate-500 tracking-wider">Secured Connection</span>
              </div>
              <div className="flex items-center gap-1.5 hidden sm:flex">
                <span className="material-symbols-outlined text-[14px] text-slate-400">memory</span>
                <span className="text-[10px] uppercase font-headline font-bold text-slate-500 tracking-wider">Gemini 1.5 Pro Enabled</span>
              </div>
            </div>
            <span className="text-[10px] text-slate-400 font-body">Deep Insights Copilot Architecture</span>
          </div>
        </form>
      </div>
    </>
  );
}
