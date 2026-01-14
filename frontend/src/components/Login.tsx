import { useState } from 'react';

interface LoginProps {
    onLogin: (username: string) => void;
}

export const Login = ({ onLogin }: LoginProps) => {
    const [username, setUsername] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (username.trim()) {
            onLogin(username.trim());
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="login-header">
                    <h1 className="login-title">WebSocket Chat</h1>
                    <p className="login-subtitle">
                        Join the conversation in real-time
                    </p>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="username" className="form-label">
                            Choose your username
                        </label>
                        <input
                            id="username"
                            type="text"
                            className="form-input"
                            placeholder="Enter your username..."
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            autoFocus
                            maxLength={20}
                        />
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={!username.trim()}
                    >
                        <span>Continue</span>
                        <span>→</span>
                    </button>
                </form>
            </div>
        </div>
    );
};
