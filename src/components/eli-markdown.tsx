'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface EliMarkdownProps {
  content: string;
}

export function EliMarkdown({ content }: EliMarkdownProps) {
  return (
    <ReactMarkdown
      components={{
        p: ({ children }) => (
          <p className="text-[#1e293b]/90 leading-relaxed mb-2 last:mb-0">{children}</p>
        ),
        strong: ({ children }) => (
          <strong className="text-[#1e293b] font-semibold">{children}</strong>
        ),
        em: ({ children }) => (
          <em className="text-[#475569] italic">{children}</em>
        ),
        ul: ({ children }) => (
          <ul className="space-y-1 mb-2 ml-1">{children}</ul>
        ),
        ol: ({ children }) => (
          <ol className="space-y-1 mb-2 ml-1">{children}</ol>
        ),
        li: ({ children }) => (
          <li className="flex gap-2 text-[#1e293b]/90 leading-relaxed">
            <span className="text-[#7c3aed] mt-0.5 flex-shrink-0">•</span>
            <span>{children}</span>
          </li>
        ),
        h1: ({ children }) => (
          <h1 className="text-lg font-bold text-[#1e293b] mt-4 mb-2">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-base font-bold text-[#1e293b] mt-3 mb-1.5">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-sm font-semibold text-[#1e293b] mt-2 mb-1">{children}</h3>
        ),
        code: ({ className, children, ...props }) => {
          const match = /language-(\w+)/.exec(className || '');
          const inline = !match;
          if (inline) {
            return (
              <code
                className="px-1.5 py-0.5 rounded text-[11px] font-mono bg-[#f1f5f9] text-[#7c3aed]"
                {...props}
              >
                {children}
              </code>
            );
          }
          return (
            <div className="my-3 rounded-lg overflow-hidden border border-[#e2e8f0]">
              <div className="flex items-center justify-between px-4 py-2 bg-[#f1f5f9] border-b border-[#e2e8f0]">
                <span className="text-[10px] font-mono text-[#64748b]">{match[1]}</span>
              </div>
              <SyntaxHighlighter
                style={oneDark}
                language={match[1]}
                PreTag="div"
                customStyle={{
                  margin: 0,
                  padding: '12px 16px',
                  background: '#1e293b',
                  fontSize: '12px',
                  lineHeight: '1.6',
                }}
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            </div>
          );
        },
        a: ({ href, children }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#7c3aed] hover:underline"
          >
            {children}
          </a>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-2 border-[#7c3aed] pl-3 my-2 text-[#64748b] italic">
            {children}
          </blockquote>
        ),
        hr: () => (
          <hr className="border-t border-[#e2e8f0] my-3" />
        ),
        table: ({ children }) => (
          <div className="overflow-x-auto my-3 rounded-lg border border-[#e2e8f0]">
            <table className="w-full text-sm">{children}</table>
          </div>
        ),
        th: ({ children }) => (
          <th className="px-3 py-2 text-left bg-[#f1f5f9] text-[#1e293b] font-semibold border-b border-[#e2e8f0]">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td className="px-3 py-2 text-[#1e293b]/80 border-b border-[#e2e8f0]">
            {children}
          </td>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
