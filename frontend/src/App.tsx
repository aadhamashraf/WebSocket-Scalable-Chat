import { useState } from 'react';
import { Login } from './components/Login';
import { RoomSelector } from './components/RoomSelector';
import { ChatRoom } from './components/ChatRoom';
import './index.css';

function App() {
    const [username, setUsername] = useState<string>('');
    const [currentRoomId, setCurrentRoomId] = useState<string>('');
    const [currentRoomName, setCurrentRoomName] = useState<string>('');

    const handleLogin = (name: string) => {
        setUsername(name);
        // Auto-select first room (General)
        setCurrentRoomId('general');
        setCurrentRoomName('General');
    };

    const handleRoomSelect = (roomId: string) => {
        setCurrentRoomId(roomId);
        // Find room name from the room list
        // This is a simple approach; in production, you'd pass the full room object
        const roomNames: { [key: string]: string } = {
            general: 'General',
            random: 'Random',
            tech: 'Tech Talk',
        };
        setCurrentRoomName(roomNames[roomId] || roomId);
    };

    if (!username) {
        return <Login onLogin={handleLogin} />;
    }

    return (
        <div className="app">
            <RoomSelector
                username={username}
                currentRoomId={currentRoomId}
                onRoomSelect={handleRoomSelect}
            />

            {currentRoomId && (
                <ChatRoom
                    roomId={currentRoomId}
                    roomName={currentRoomName}
                    username={username}
                />
            )}
        </div>
    );
}

export default App;
