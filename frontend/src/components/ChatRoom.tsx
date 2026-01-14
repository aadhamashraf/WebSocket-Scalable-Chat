import { useState, useEffect, useRef } from 'react';
import { Message } from '../types';
import { useWebSocket } from '../hooks/useWebSocket';
import { api } from '../api';

interface ChatRoomProps {
    roomId: string;
    roomName: string;
    username: string;
}

export const ChatRoom = ({ roomId, roomName, username }: ChatRoomProps) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputMessage, setInputMessage] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const { isConnected, isConnecting, sendMessage } = useWebSocket({
        url: api.getWebSocketUrl(roomId, username),
        onMessage: (message) => {
            setMessages((prev) => [...prev, message]);
        },
        onOpen: () => {
            console.log('Connected to room:', roomName);
        },
        onClose: () => {
            console.log('Disconnected from room:', roomName);
        },
    });

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Clear messages when room changes
    useEffect(() => {
        setMessages([]);
    }, [roomId]);

    const handleSendMessage = (e: React.FormEvent) => {
        e.preventDefault();

        if (!inputMessage.trim() || !isConnected) {
            return;
        }

        sendMessage(inputMessage.trim());
        setInputMessage('');
    };

    const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage(e);
        }
    };

    const formatTime = (timestamp: string) => {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const getInitials = (name: string) => {
        return name.charAt(0).toUpperCase();
    };

    return (
        <div className="chat-container">
            <div className="chat-header">
                <h2 className="chat-room-title">{roomName}</h2>
                <div className="chat-room-meta">
                    {isConnecting && 'Connecting...'}
                    {isConnected && 'Connected'}
                    {!isConnected && !isConnecting && 'Disconnected'}
                </div>
            </div>

            <div className="messages-container">
                {messages.length === 0 && (
                    <div className="message system">
                        <div className="message-text">
                            Welcome to {roomName}! Start chatting below.
                        </div>
                    </div>
                )}

                {messages.map((message, index) => {
                    if (message.message_type === 'join' || message.message_type === 'leave') {
                        return (
                            <div key={index} className="message system">
                                <div className="message-text">{message.content}</div>
                            </div>
                        );
                    }

                    return (
                        <div key={index} className="message">
                            <div className="message-avatar">
                                {getInitials(message.username)}
                            </div>
                            <div className="message-content">
                                <div className="message-header">
                                    <span className="message-author">{message.username}</span>
                                    <span className="message-time">
                                        {formatTime(message.timestamp)}
                                    </span>
                                </div>
                                <div className="message-text">{message.content}</div>
                            </div>
                        </div>
                    );
                })}

                <div ref={messagesEndRef} />
            </div>

            <div className="message-input-container">
                <form onSubmit={handleSendMessage} className="message-input-wrapper">
                    <textarea
                        className="message-input"
                        placeholder="Type a message..."
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        rows={1}
                        disabled={!isConnected}
                    />
                    <button
                        type="submit"
                        className="btn-send"
                        disabled={!inputMessage.trim() || !isConnected}
                        title="Send message"
                    >
                        ↑
                    </button>
                </form>
            </div>
        </div>
    );
};
