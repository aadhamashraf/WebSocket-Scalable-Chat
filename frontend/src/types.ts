export interface Message {
    user_id: string;
    username: string;
    room_id: string;
    content: string;
    message_type: 'chat' | 'join' | 'leave' | 'typing' | 'system';
    timestamp: string;
}

export interface Room {
    id: string;
    name: string;
    created_at: string;
    member_count: number;
}

export interface User {
    id: string;
    username: string;
    current_room?: string;
}
