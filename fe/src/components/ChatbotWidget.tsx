import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Bot, User, Loader2, Trash2 } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import { lcChatApi } from '../services/api';

type Message = {
  id: string;
  sender: 'user' | 'bot';
  text: string;
};

interface ChatbotWidgetProps {
  user?: any;
}

export function ChatbotWidget({ user }: ChatbotWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputVal, setInputVal] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isFetchingHistory, setIsFetchingHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const initialGreeting: Message = {
    id: 'greeting',
    sender: 'bot',
    text: 'Chào bạn! Mình là trợ lý AI của TicketX. Mình có thể giúp gì cho bạn hôm nay?',
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, isFetchingHistory]);

  // Fetch history when widget opens and user is logged in
  useEffect(() => {
    if (isOpen && user) {
      loadHistory();
    } else if (!isOpen && !user) {
        // Reset to initial if not logged in and closed (optional)
        setMessages([initialGreeting]);
    } else if (messages.length === 0) {
        setMessages([initialGreeting]);
    }
  }, [isOpen, user]);

  const loadHistory = async () => {
    setIsFetchingHistory(true);
    try {
      const history = await lcChatApi.getHistory();
      if (history && history.length > 0) {
        const mappedMessages: Message[] = history.map((m: any, idx: number) => ({
          id: `hist-${idx}`,
          sender: m.role === 'human' ? 'user' : 'bot',
          text: m.content
        }));
        setMessages(mappedMessages);
      } else {
        setMessages([initialGreeting]);
      }
    } catch (error) {
      console.error("Failed to load chat history:", error);
      setMessages([initialGreeting]);
    } finally {
      setIsFetchingHistory(false);
    }
  };

  const handleClearHistory = async () => {
    if (!user) {
        setMessages([initialGreeting]);
        return;
    }

    if (window.confirm("Bạn có chắc chắn muốn xóa toàn bộ lịch sử trò chuyện?")) {
        try {
            await lcChatApi.clearHistory();
            setMessages([initialGreeting]);
        } catch (error) {
            alert("Không thể xóa lịch sử lúc này.");
        }
    }
  };

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!inputVal.trim() || isLoading) return;

    const userText = inputVal.trim();
    const newUserMsg: Message = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: userText,
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setInputVal('');
    setIsLoading(true);

    try {
      const response = await lcChatApi.ask(userText);
      
      if (!response.ok) {
        throw new Error('Failed to connect to assistant');
      }

      // Read the stream
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let streamedText = "";
      let buffer = ""; 
      let botMsgId = ""; // We'll set this when we get the first token

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          
          const parts = buffer.split('\n\n');
          buffer = parts.pop() || "";

          for (const part of parts) {
            const lines = part.split('\n');
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const jsonStr = line.slice(6).trim();
                if (!jsonStr) continue;

                try {
                  const data = JSON.parse(jsonStr);
                  if (data.token) {
                    streamedText += data.token;
                    
                    if (!botMsgId) {
                      // First data payload arrived: Create the bubble and stop loading indicator
                      botMsgId = `bot-${Date.now()}`;
                      setIsLoading(false);
                      setMessages((prev) => [...prev, {
                        id: botMsgId,
                        sender: 'bot',
                        text: streamedText,
                      }]);
                    } else {
                      // Subsequent tokens: Update the existing bubble
                      setMessages((prev) => 
                        prev.map(m => m.id === botMsgId ? { ...m, text: streamedText } : m)
                      );
                    }
                  } else if (data.done) {
                    setIsLoading(false);
                  } else if (data.error) {
                    throw new Error(data.error);
                  }
                } catch (e: any) {
                  if (e.message?.includes('Access denied') || e.message?.includes('403')) {
                      const errMsg = "Lỗi Groq API (403): Truy cập bị từ chối. Vui lòng kiểm tra API Key hoặc vùng hỗ trợ.";
                      // If bubble exists, update it, else add it
                      if (!botMsgId) {
                         botMsgId = `bot-${Date.now()}`;
                         setMessages((prev) => [...prev, { id: botMsgId, sender: 'bot', text: errMsg }]);
                      } else {
                         setMessages((prev) => prev.map(m => m.id === botMsgId ? { ...m, text: errMsg } : m));
                      }
                      setIsLoading(false);
                      return;
                  }
                  console.error("Parse error:", e);
                }
              }
            }
          }
        }
      }
    } catch (error: any) {
      console.error(error);
      setMessages((prev) => 
        prev.map(m => m.id.startsWith('bot-') && m.text === '' 
          ? { ...m, text: 'Đã có lỗi xảy ra khi kết nối. Vui lòng thử lại sau!' } 
          : m)
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-20 right-6 w-80 md:w-96 bg-white rounded-2xl shadow-2xl border border-navy-100 flex flex-col overflow-hidden z-50 font-sans"
            style={{ height: '500px', maxHeight: '80vh' }}
          >
            {/* Header */}
            <div className="bg-navy-900 text-white p-4 flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-coral-500 rounded-full flex items-center justify-center">
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-lg leading-tight">TicketX AI</h3>
                  <p className="text-xs text-navy-200">
                    {user ? `Chào ${user.full_name.split(' ')[0]}` : 'Luôn sẵn sàng hỗ trợ'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-1">
                {user && (
                    <button
                        onClick={handleClearHistory}
                        title="Xóa lịch sử"
                        className="p-2 hover:bg-navy-800 rounded-full transition-colors text-navy-200 hover:text-red-400"
                    >
                        <Trash2 className="w-4 h-4" />
                    </button>
                )}
                <button
                    onClick={() => setIsOpen(false)}
                    className="p-2 hover:bg-navy-800 rounded-full transition-colors"
                >
                    <X className="w-5 h-5 text-navy-200 hover:text-white" />
                </button>
              </div>
            </div>

            {/* Chat Body */}
            <div className="flex-1 p-4 overflow-y-auto bg-navy-50 flex flex-col gap-4">
              {isFetchingHistory ? (
                  <div className="flex flex-col items-center justify-center h-full gap-2 text-navy-400">
                      <Loader2 className="w-6 h-6 animate-spin" />
                      <span className="text-xs">Đang tải lịch sử...</span>
                  </div>
              ) : (
                messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex gap-3 ${
                        msg.sender === 'user' ? 'flex-row-reverse' : ''
                      }`}
                    >
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                          msg.sender === 'user'
                            ? 'bg-blue-100 text-blue-600'
                            : 'bg-coral-100 text-coral-600'
                        }`}
                      >
                        {msg.sender === 'user' ? (
                          <User className="w-4 h-4" />
                        ) : (
                          <Bot className="w-4 h-4" />
                        )}
                      </div>
                      <div
                        className={`px-4 py-2.5 rounded-2xl max-w-[75%] text-sm leading-relaxed whitespace-pre-wrap ${
                          msg.sender === 'user'
                            ? 'bg-blue-600 text-white rounded-tr-none'
                            : 'bg-white border border-navy-100 text-navy-800 rounded-tl-none shadow-sm'
                        }`}
                      >
                        {msg.text}
                      </div>
                    </div>
                  ))
              )}
              
              {isLoading && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-coral-100 text-coral-600 flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="px-4 py-3 rounded-2xl bg-white border border-navy-100 rounded-tl-none shadow-sm flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-navy-400" />
                    <span className="text-xs text-navy-400">Đang gõ...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Footer */}
            <div className="p-4 bg-white border-t border-navy-100">
              <form
                onSubmit={handleSend}
                className="flex items-center gap-2 bg-navy-50 rounded-full px-4 py-2 border border-navy-100 focus-within:border-blue-400 transition-colors"
              >
                <input
                  type="text"
                  value={inputVal}
                  onChange={(e) => setInputVal(e.target.value)}
                  placeholder="Gõ tin nhắn..."
                  className="flex-1 bg-transparent py-2 text-sm outline-none text-navy-900 placeholder:text-navy-400"
                />
                <button
                  type="submit"
                  disabled={!inputVal.trim() || isLoading || isFetchingHistory}
                  className="p-2 text-blue-600 hover:bg-blue-100 rounded-full transition-colors disabled:opacity-50 disabled:hover:bg-transparent"
                >
                  <Send className="w-5 h-5" />
                </button>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Button */}
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-coral-500 hover:bg-coral-600 shadow-lg hover:shadow-orange-500/30 rounded-full flex items-center justify-center text-white transition-all z-50 hover:scale-105 active:scale-95"
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.div
              key="close"
              initial={{ opacity: 0, rotate: -90 }}
              animate={{ opacity: 1, rotate: 0 }}
              exit={{ opacity: 0, rotate: 90 }}
              transition={{ duration: 0.15 }}
            >
              <X className="w-6 h-6" />
            </motion.div>
          ) : (
            <motion.div
              key="chat"
              initial={{ opacity: 0, rotate: 90 }}
              animate={{ opacity: 1, rotate: 0 }}
              exit={{ opacity: 0, rotate: -90 }}
              transition={{ duration: 0.15 }}
            >
              <MessageSquare className="w-6 h-6" />
            </motion.div>
          )}
        </AnimatePresence>
      </button>
    </>
  );
}

