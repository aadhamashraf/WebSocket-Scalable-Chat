import { useState, useEffect, useCallback, useRef } from 'react';
import { Message } from '../types';

interface UseWebSocketProps {
    url: string;
    onMessage?: (message: Message) => void;
    onOpen?: () => void;
    onClose?: () => void;
    onError?: (error: Event) => void;
}

export const useWebSocket = ({
    url,
    onMessage,
    onOpen,
    onClose,
    onError
}: UseWebSocketProps) => {
    const [isConnected, setIsConnected] = useState(false);
    const [isConnecting, setIsConnecting] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<number>();
    const reconnectAttemptsRef = useRef(0);
    const maxReconnectAttempts = 5;
    const reconnectDelay = 2000;

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return;
        }

        setIsConnecting(true);

        try {
            const ws = new WebSocket(url);

            ws.onopen = () => {
                console.log('WebSocket connected');
                setIsConnected(true);
                setIsConnecting(false);
                reconnectAttemptsRef.current = 0;
                onOpen?.();
            };

            ws.onmessage = (event) => {
                try {
                    const message: Message = JSON.parse(event.data);
                    onMessage?.(message);
                } catch (error) {
                    console.error('Failed to parse message:', error);
                }
            };

            ws.onclose = () => {
                console.log('WebSocket disconnected');
                setIsConnected(false);
                setIsConnecting(false);
                onClose?.();

                // Attempt to reconnect
                if (reconnectAttemptsRef.current < maxReconnectAttempts) {
                    reconnectAttemptsRef.current++;
                    console.log(`Reconnecting... Attempt ${reconnectAttemptsRef.current}`);
                    reconnectTimeoutRef.current = window.setTimeout(() => {
                        connect();
                    }, reconnectDelay);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                onError?.(error);
            };

            wsRef.current = ws;
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            setIsConnecting(false);
        }
    }, [url, onMessage, onOpen, onClose, onError]);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }

        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }

        setIsConnected(false);
        setIsConnecting(false);
    }, []);

    const sendMessage = useCallback((message: string) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(message);
        } else {
            console.warn('WebSocket is not connected');
        }
    }, []);

    useEffect(() => {
        connect();

        return () => {
            disconnect();
        };
    }, [connect, disconnect]);

    return {
        isConnected,
        isConnecting,
        sendMessage,
        disconnect,
        reconnect: connect
    };
};
