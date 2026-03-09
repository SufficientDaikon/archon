"use client";

import { useState } from "react";

interface InstallCommandProps {
  command: string;
  label?: string;
  compact?: boolean;
}

export default function InstallCommand({
  command,
  label,
  compact = false,
}: InstallCommandProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(command);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textArea = document.createElement("textarea");
      textArea.value = command;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className={compact ? "" : "space-y-1"}>
      {label && <p className="text-xs text-brand-muted font-medium">{label}</p>}
      <div className="flex items-center gap-2 bg-black/40 border border-white/10 rounded-lg overflow-hidden group">
        <code
          className={`flex-1 font-mono text-brand-cyan ${compact ? "text-xs px-3 py-2" : "text-sm px-4 py-3"} truncate`}
        >
          {command}
        </code>
        <button
          onClick={handleCopy}
          className={`${compact ? "px-2 py-2" : "px-3 py-3"} text-brand-muted hover:text-brand-text transition-all border-l border-white/10 hover:bg-white/5 shrink-0`}
          aria-label={copied ? "Copied!" : "Copy to clipboard"}
          title={copied ? "Copied!" : "Copy to clipboard"}
        >
          {copied ? (
            <svg
              className="w-4 h-4 text-green-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          ) : (
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}
