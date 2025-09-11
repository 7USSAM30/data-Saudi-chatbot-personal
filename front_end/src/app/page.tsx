'use client';

import { useState, useRef, useEffect } from 'react';
import { Typewriter } from 'react-simple-typewriter';
import Image from 'next/image';
import ReactMarkdown from 'react-markdown';

export default function Home() {
  const [messages, setMessages] = useState<{ sender: 'user' | 'bot', text: string, context?: string[] }[]>([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    setMessages((msgs) => [...msgs, { sender: 'user', text: input }]);
    const userInput = input;
    setInput('');
    setMessages((msgs) => [
      ...msgs,
      { sender: 'bot', text: 'Thinking...' }
    ]);
    try {
      const res = await fetch('http://localhost:8000/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userInput }),
      });
      const data = await res.json();
      setMessages((msgs) => [
        ...msgs.slice(0, -1), // Remove "Thinking..."
        { sender: 'bot', text: data.answer, context: data.context }
      ]);
    } catch {
      setMessages((msgs) => [
        ...msgs.slice(0, -1),
        { sender: 'bot', text: 'Sorry, there was an error connecting to the server.' }
      ]);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-start pt-16" style={{ background: "transparent" }}>
      <div className="flex flex-col items-center mb-8 animate-fadein">
        <Image
          src="/datasaudi-logo.png"
          alt="DataSaudi Logo"
          width={80}
          height={80}
          className="mb-4"
        />
        <h1 className="text-2xl md:text-3xl font-bold text-blue-900 text-center transition-all duration-500">
          <Typewriter
            words={[
              'Welcome to DataSaudi Chatbot',
              'Your gateway to Saudi Arabia\'s data.',
              'Ask me about economy, population, and more!',
            ]}
            loop={0}
            cursor
            cursorStyle="_"
            typeSpeed={70}
            deleteSpeed={50}
            delaySpeed={2000}
          />
        </h1>
      </div>
      <div className="w-full max-w-xl flex flex-col rounded-3xl shadow-2xl p-0 animate-fadein border border-white/30" style={{ minHeight: 500, height: 500, background: 'rgba(255,255,255,0.18)', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)', boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)' }}>
        {/* Chat area */}
        <div className="flex-1 overflow-y-auto px-6 pt-6" style={{ minHeight: 0 }}>
          {messages.length === 0 && (
            <div className="text-gray-400 text-center mt-10">Start the conversation below…</div>
          )}
          {messages.map((msg, idx) => (
            <div key={idx} className={`mb-2 flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className="flex items-end gap-2">
                {msg.sender === 'bot' && (
                  <Image
                    src="/datasaudi-logo.png"
                    alt="Bot"
                    width={32}
                    height={32}
                    className="w-8 h-8 rounded-full bg-white border border-blue-300 object-cover"
                    style={{ background: '#fff' }}
                  />
                )}
                <div className={`px-4 py-2 rounded-2xl max-w-xs break-words shadow ${msg.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-900'}`}>
                  {msg.sender === 'bot' ? (
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                          strong: ({ children }) => <strong className="font-bold text-gray-900">{children}</strong>,
                          ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                          li: ({ children }) => <li className="text-sm">{children}</li>,
                          em: ({ children }) => <em className="italic text-gray-600 text-xs">{children}</em>,
                          hr: () => <hr className="my-2 border-gray-300" />,
                        }}
                      >
                        {msg.text}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    msg.text
                  )}
                  {/* Show context if present and this is a bot message */}
                  {msg.sender === 'bot' && msg.context && msg.context.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-300">
                      <div className="text-xs text-gray-600 font-semibold mb-1">Sources:</div>
                      <div className="text-xs text-gray-500">
                        {msg.context.map((source, idx) => (
                          <div key={idx} className="truncate" title={source}>
                            • {source}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                {msg.sender === 'user' && (
                  <div className="w-8 h-8 flex items-center justify-center rounded-full bg-gray-300 text-2xl">
                    🧑
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        {/* Input area at the bottom */}
        <div className="flex gap-2 px-6 py-4 border-t border-gray-200 bg-white bg-opacity-90 rounded-b-3xl" style={{}}>
          <input
            className="flex-1 px-4 py-3 rounded-2xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 text-gray-900 text-lg"
            type="text"
            placeholder="Type your question…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            className="px-6 py-3 rounded-2xl bg-blue-700 text-white font-semibold hover:bg-blue-800 transition text-lg"
            onClick={sendMessage}
          >
            Send
          </button>
        </div>
      </div>
      <style jsx global>{`
        @keyframes fadein {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: none; }
        }
        .animate-fadein {
          animation: fadein 0.8s cubic-bezier(0.4,0,0.2,1);
        }
      `}</style>
    </main>
  );
}
