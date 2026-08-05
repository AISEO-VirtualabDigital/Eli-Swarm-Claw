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
          <p className="text-[#f5f6ff]/90 leading-relaxed mb-2 last:mb-0">{children}</p>
        ),
        strong: ({ children }) => (
          <strong className="text-[#f5f6ff] font-semibold">{children}</strong>
        ),
        em: ({ children }) => (
          <em className="text-[#c4c9e8] italic">{children}</em>
        ),
        ul: ({ children }) => (
          <ul className="space-y-1 mb-2 ml-1">{children}</ul>
        ),
        ol: ({ children }) => (
          <ol className="space-y-1 mb-2 ml-1">{children}</ol>
        ),
        li: ({ children }) => (
          <li className="flex gap-2 text-[#f5f6ff]/90 leading-relaxed">
            <span className="text-[#8b5cf6] mt-0.5 flex-shrink-0">•</span>
            <span>{children}</span>
          </li>
        ),
        h1: ({ children }) => (
          <h1 className="text-lg font-bold text-[#f5f6ff] mt-4 mb-2">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-base font-bold text-[#f5f6ff] mt-3 mb-1.5">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-sm font-semibold text-[#f5f6ff] mt-2 mb-1">{children}</h3>
        ),
        code: ({ className, children, ...props }) => {
          const match = /language-(\w+)/.exec(className || '');
          const inline = !match;
          if (inline) {
            return (
              <code
                className="px-1.5 py-0.5 rounded text-[11px] font-mono bg-[#12162a] text-[#50d8ff]"
                {...props}
              >
                {children}
              </code>
            );
          }
          return (
            <div className="my-3 rounded-lg overflow-hidden border border-[#252a46]">
              <div className="flex items-center justify-between px-4 py-2 bg-[#12162a] border-b border-[#252a46]">
                <span className="text-[10px] font-mono text-[#9ba4c5]">{match[1]}</span>
              </div>
              <SyntaxHighlighter
                style={oneDark}
                language={match[1]}
                PreTag="div"
                customStyle={{
                  margin: 0,
                  padding: '12px 16px',
                  background: '#0a0c18',
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
            className="text-[#50d8ff] hover:underline"
          >
            {children}
          </a>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-2 border-[#8b5cf6] pl-3 my-2 text-[#9ba4c5] italic">
            {children}
          </blockquote>
        ),
        hr: () => (
          <hr className="border-t border-[#252a46] my-3" />
        ),
        table: ({ children }) => (
          <div className="overflow-x-auto my-3 rounded-lg border border-[#252a46]">
            <table className="w-full text-sm">{children}</table>
          </div>
        ),
        th: ({ children }) => (
          <th className="px-3 py-2 text-left bg-[#12162a] text-[#f5f6ff] font-semibold border-b border-[#252a46]">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td className="px-3 py-2 text-[#f5f6ff]/80 border-b border-[#252a46]">
            {children}
          </td>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
