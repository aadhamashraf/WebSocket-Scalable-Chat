const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export const api = {
    async getRooms() {
        const response = await fetch(`${API_BASE_URL}/api/rooms`);
        if (!response.ok) {
            throw new Error('Failed to fetch rooms');
        }
        return response.json();
    },

    async createRoom(name: string) {
        const response = await fetch(`${API_BASE_URL}/api/rooms`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name }),
        });
        if (!response.ok) {
            throw new Error('Failed to create room');
        }
        return response.json();
    },

    getWebSocketUrl(roomId: string, username: string) {
        return `${WS_BASE_URL}/ws/${roomId}?username=${encodeURIComponent(username)}`;
    },
};
