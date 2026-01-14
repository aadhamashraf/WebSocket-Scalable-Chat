import { useState, useEffect } from 'react';
import { Room } from '../types';
import { api } from '../api';

interface RoomSelectorProps {
    username: string;
    currentRoomId?: string;
    onRoomSelect: (roomId: string) => void;
}

export const RoomSelector = ({
    username,
    currentRoomId,
    onRoomSelect,
}: RoomSelectorProps) => {
    const [rooms, setRooms] = useState<Room[]>([]);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newRoomName, setNewRoomName] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const loadRooms = async () => {
        try {
            const data = await api.getRooms();
            setRooms(data);
        } catch (error) {
            console.error('Failed to load rooms:', error);
        }
    };

    useEffect(() => {
        loadRooms();
        const interval = setInterval(loadRooms, 5000); // Refresh every 5 seconds
        return () => clearInterval(interval);
    }, []);

    const handleCreateRoom = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newRoomName.trim()) return;

        setIsLoading(true);
        try {
            const newRoom = await api.createRoom(newRoomName.trim());
            setRooms([...rooms, newRoom]);
            setNewRoomName('');
            setShowCreateModal(false);
            onRoomSelect(newRoom.id);
        } catch (error) {
            console.error('Failed to create room:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            <div className="sidebar">
                <div className="sidebar-header">
                    <h2 className="sidebar-title">Chat Rooms</h2>

                    <div className="user-info">
                        <div className="user-avatar">
                            {username.charAt(0).toUpperCase()}
                        </div>
                        <div className="user-details">
                            <div className="user-name">{username}</div>
                            <div className="user-status">
                                <span className="status-dot"></span>
                                Online
                            </div>
                        </div>
                    </div>
                </div>

                <div className="rooms-container">
                    <div className="rooms-header">
                        <span className="rooms-title">Rooms</span>
                        <button
                            className="btn-icon"
                            onClick={() => setShowCreateModal(true)}
                            title="Create new room"
                        >
                            +
                        </button>
                    </div>

                    <ul className="room-list">
                        {rooms.map((room) => (
                            <li
                                key={room.id}
                                className={`room-item ${currentRoomId === room.id ? 'active' : ''}`}
                                onClick={() => onRoomSelect(room.id)}
                            >
                                <div className="room-name">{room.name}</div>
                                <div className="room-meta">
                                    {room.member_count} {room.member_count === 1 ? 'member' : 'members'}
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {showCreateModal && (
                <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3 className="modal-title">Create New Room</h3>
                        </div>

                        <form onSubmit={handleCreateRoom}>
                            <div className="form-group">
                                <label htmlFor="roomName" className="form-label">
                                    Room Name
                                </label>
                                <input
                                    id="roomName"
                                    type="text"
                                    className="form-input"
                                    placeholder="Enter room name..."
                                    value={newRoomName}
                                    onChange={(e) => setNewRoomName(e.target.value)}
                                    autoFocus
                                    maxLength={30}
                                />
                            </div>

                            <div className="modal-actions">
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={() => setShowCreateModal(false)}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="btn btn-primary"
                                    disabled={!newRoomName.trim() || isLoading}
                                >
                                    {isLoading ? 'Creating...' : 'Create Room'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </>
    );
};
