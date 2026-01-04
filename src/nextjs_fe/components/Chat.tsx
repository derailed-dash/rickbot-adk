import React, { useState, useEffect, useRef } from 'react';
import { useSession, signIn, signOut } from "next-auth/react"
import {
    Box,
    TextField,
    Button,
    List,
    ListItem,
    ListItemText,
    ListItemAvatar,
    Avatar,
    Typography,
    Paper,
    IconButton,
    LinearProgress
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import Link from 'next/link';
import PortalAnimation from './PortalAnimation';
import Header from './Header';
import Thinking from './Thinking';
import { Personality, Message, ToolCall, ToolResponse } from '../types/chat';

const initialPersonalities: Personality[] = [
    { 
        name: 'Rick', 
        description: 'Rick Sanchez', 
        avatar: '/avatars/rick.png',
        title: "I'm Rickbot! Wubba Lubba Dub Dub!",
        overview: "I'm Rick Sanchez. The smartest man in the universe. Cynical and sarcastic. People are dumb.",
        welcome: "Ask me something. Or don't. Whatever.",
        prompt_question: "What do you want?"
    }
];

interface AttachmentItemProps {
    file: File;
}

const AttachmentItem: React.FC<AttachmentItemProps> = ({ file }) => {
    const [objectUrl, setObjectUrl] = useState<string | null>(null);

    useEffect(() => {
        if (!file) return;
        const url = URL.createObjectURL(file);
        setObjectUrl(url);

        return () => {
            URL.revokeObjectURL(url);
        };
    }, [file]);

    if (file.type.startsWith('image/') || file.type.startsWith('video/')) {
         if (!objectUrl) return null;
         if (file.type.startsWith('image/')) {
            return <Box component="img" src={objectUrl} sx={{ maxWidth: '100%', maxHeight: '300px', borderRadius: 1, display: 'block' }} />;
         } else {
            return <Box component="video" src={objectUrl} controls sx={{ maxWidth: '100%', maxHeight: '300px', borderRadius: 1, display: 'block' }} />;
         }
    } else {
        return (
            <Paper variant="outlined" sx={{ p: 1, display: 'flex', alignItems: 'center', gap: 1, bgcolor: 'rgba(255,255,255,0.05)' }}>
                <AttachFileIcon fontSize="small" />
                <Typography variant="caption">{file.name}</Typography>
            </Paper>
        );
    }
};

export default function Chat() {
    const { data: session, status } = useSession()
    const [messages, setMessages] = useState<Message[]>([]);
    const [personalities, setPersonalities] = useState<Personality[]>(initialPersonalities);
    const [inputValue, setInputValue] = useState('');
    const [selectedPersonality, setSelectedPersonality] = useState<Personality>(initialPersonalities[0]);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [botAction, setBotAction] = useState<string | null>(null);
    const [activeTool, setActiveTool] = useState<{name: string, status: 'running' | 'completed'} | null>(null);
    const [files, setFiles] = useState<File[]>([]);
    const messagesEndRef = useRef<null | HTMLDivElement>(null);
    const [streamingText, setStreamingText] = useState('');
    const [showPortal, setShowPortal] = useState(false);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, streamingText, botAction]);

    useEffect(() => {
        const fetchPersonalities = async () => {
            const token = session?.idToken || session?.accessToken || "";
            // console.log("Token:", token);
            try {
                const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/personas`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                if (response.data && Array.isArray(response.data)) {
                    setPersonalities(response.data);
                    // Update selected personality object if it was the default or exists in the new list
                    const updatedSelected = response.data.find((p: Personality) => p.name === selectedPersonality.name);
                    if (updatedSelected) {
                        setSelectedPersonality(updatedSelected);
                    }
                }
            } catch (error: any) {
                console.error("Failed to fetch personalities:", error);
                if (error.response?.status === 401 || error.response?.status === 403) {
                    console.warn("Auth failure detected in fetchPersonalities. Signing out.");
                    signOut();
                }
            }
        };

        if (session) {
            fetchPersonalities();
        }
    }, [session]);



    const handleSendMessage = async () => {
        if (!inputValue.trim() && files.length === 0) return;

        const newMessage: Message = {
            id: Date.now().toString(),
            text: inputValue,
            sender: 'user',
            attachments: files.length > 0 ? [...files] : []
        };

        setMessages(prev => [...prev, newMessage]);
        setInputValue('');
        setFiles([]);
        setLoading(true);
        setStreamingText('');
        setBotAction('Thinking...');
        setActiveTool(null);
        setShowPortal(true);
        setTimeout(() => setShowPortal(false), 1000);

        try {
            const token = session?.idToken || session?.accessToken || "";
            
            const formData = new FormData();
            formData.append('prompt', newMessage.text);
            formData.append('personality', selectedPersonality.name);
            if (sessionId) {
                formData.append('session_id', sessionId);
            }
            if (newMessage.attachments) {
                newMessage.attachments.forEach(f => {
                    formData.append('files', f);
                });
            }

            // Streaming implementation
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/chat_stream`, {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${token}`
                },
                body: formData,
            });

            if (response.status === 401 || response.status === 403) {
                console.warn("Auth failure detected in handleSendMessage. Signing out.");
                signOut();
                return;
            }

            if (!response.body) return;

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let accumulatedText = '';
            let currentSessionId = sessionId;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.session_id && !currentSessionId) {
                                currentSessionId = data.session_id;
                                setSessionId(data.session_id);
                            }
                            if (data.tool_call) {
                                const toolCall = data.tool_call as ToolCall;
                                setBotAction(`Using tool: ${toolCall.name}...`);
                                setActiveTool({ name: toolCall.name, status: 'running' });
                            }
                            if (data.tool_response) {
                                const toolResponse = data.tool_response as ToolResponse;
                                // Ideally we show "Tool X finished" briefly, but maybe just clear active tool
                                // or update status. For now, keep showing "Using tool X..." until next tool or response starts
                                setActiveTool(prev => prev ? { ...prev, status: 'completed' } : null);
                            }
                            if (data.agent_transfer) {
                                setBotAction(`Transferring to agent: ${data.agent_transfer}...`);
                                setActiveTool(null);
                            }
                            if (data.chunk) {
                                setBotAction('Responding...');
                                accumulatedText += data.chunk;
                                setStreamingText(accumulatedText);
                                setActiveTool(null); // Clear tool when response starts
                            }
                        } catch (e) {
                            console.error("Error parsing JSON chunk", e);
                        }
                    }
                }
            }

             const botMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: accumulatedText,
                sender: 'bot',
                personality: selectedPersonality.name
            };
            setMessages(prev => [...prev, botMessage]);
            setStreamingText('');
            setBotAction(null);
            setActiveTool(null);

        } catch (error) {
            console.error('Error sending message:', error);
            setBotAction(null);
            setActiveTool(null);
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: "Sorry, I encountered an error.",
                sender: 'bot',
                personality: selectedPersonality.name
            };
             setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleClearChat = () => {
        setMessages([]);
        setSessionId(null);
        setStreamingText('');
        setBotAction(null);
    };

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files) {
            setFiles(prev => [...prev, ...Array.from(event.target.files!)]);
        }
    };

    if (status === "loading") {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', bgcolor: '#121212' }}>
                <LinearProgress sx={{ width: '50%' }} />
            </Box>
        )
    }

    if (!session) {
        return (
            <Box sx={{
                height: '100vh',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                p: 2,
                backgroundImage: 'url(/galaxy_bg.png)',
                backgroundRepeat: 'repeat',
                backgroundPosition: 'center',
                backgroundSize: 'auto',
                backgroundColor: 'rgba(0,0,0,0.8)',
                backgroundBlendMode: 'overlay',
                color: 'white'
            }}>
                <Typography variant="h3" color="primary" gutterBottom>Rickbot</Typography>
                <Typography variant="h6" gutterBottom sx={{ mb: 4 }}>Wubba Lubba Dub Dub! Sign in to start chatting.</Typography>
                <Button variant="contained" color="primary" size="large" onClick={() => signIn()} sx={{ mb: 4 }}>
                    Sign In
                </Button>
                <Link href="/privacy" passHref legacyBehavior>
                    <Typography component="a" variant="body2" color="primary" sx={{ cursor: 'pointer', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
                        Privacy Policy
                    </Typography>
                </Link>
            </Box>
        )
    }

    return (
        <Box sx={{
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
            maxWidth: 'md',
            margin: '0 auto',
            p: 2,
            backgroundImage: 'url(/galaxy_bg.png)',
            backgroundRepeat: 'repeat',
            backgroundPosition: 'center',
            backgroundSize: 'auto',
            backgroundColor: 'rgba(0,0,0,0.85)',
            backgroundBlendMode: 'darken'
        }}>
            <Header 
                personalities={personalities}
                selectedPersonality={selectedPersonality}
                onPersonalityChange={(p) => setSelectedPersonality(p)}
                onClearChat={handleClearChat}
            />

            {/* Persona Profile Area */}
            <Paper elevation={3} sx={{ p: 2, mb: 2, bgcolor: '#000000', borderLeft: '4px solid', borderColor: '#000000' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Avatar 
                        src={selectedPersonality.avatar} 
                        sx={{ width: 64, height: 64 }} 
                    />
                    <Box>
                        <Typography variant="h6" color="primary.main" sx={{ fontWeight: 'bold' }}>
                            {selectedPersonality.title}
                        </Typography>
                        <Typography variant="body2" color="text.primary" sx={{ mb: 0.5 }}>
                            {selectedPersonality.overview}
                        </Typography>
                        <Typography variant="caption" color="secondary.main" sx={{ fontStyle: 'italic', fontWeight: 'bold', textShadow: '0 0 5px rgba(255, 64, 255, 0.5)' }}>
                            {selectedPersonality.welcome}
                        </Typography>
                    </Box>
                </Box>
            </Paper>

            <Paper elevation={3} sx={{ flexGrow: 1, overflow: 'auto', p: 2, mb: 2, bgcolor: 'rgba(0,0,0,0.9)' }}>
                <List>
                    {messages.map((msg) => (
                        <ListItem key={msg.id} alignItems="flex-start">
                            <ListItemAvatar>
                                <Avatar src={msg.sender === 'user' ? (session?.user?.image || '/avatars/morty.png') : `/avatars/${msg.personality?.toLowerCase()}.png`} />
                            </ListItemAvatar>
                            <ListItemText
                                primary={
                                    <Box component="span" sx={{ 
                                        fontWeight: 'bold', 
                                        color: msg.sender === 'user' ? 'secondary.main' : 'primary.main',
                                        textShadow: msg.sender === 'user' ? '0 0 5px rgba(255, 64, 255, 0.5)' : 'none'
                                    }}>
                                        {msg.sender === 'user' ? 'You' : msg.personality}
                                    </Box>
                                }
                                secondary={
                                    <Box component="span" sx={{ color: 'text.primary' }}>
                                        {msg.attachments && msg.attachments.length > 0 && (
                                            <Box sx={{ mb: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                                {msg.attachments.map((att, i) => {
                                                    if (!(att instanceof File)) return null;
                                                    return <AttachmentItem key={i} file={att} />;
                                                })}
                                            </Box>
                                        )}
                                        <ReactMarkdown
                                          components={{
                                            p: ({node, ...props}) => <span {...props} />
                                          }}
                                        >
                                          {msg.text}
                                        </ReactMarkdown>
                                    </Box>
                                }
                            />
                        </ListItem>
                    ))}
                    {loading && (
                         <ListItem alignItems="flex-start">
                            <ListItemAvatar>
                                <Avatar src={`/avatars/${selectedPersonality.name.toLowerCase()}.png`} />
                            </ListItemAvatar>
                            <ListItemText
                                primary={
                                    <Box component="span" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                                        {selectedPersonality.name}
                                    </Box>
                                }
                                secondary={
                                    <Box component="span" sx={{ color: 'text.primary' }}>
                                        <Thinking action={botAction} activeTool={activeTool} />
                                        {streamingText && (
                                            <ReactMarkdown
                                              components={{
                                                p: ({node, ...props}) => <span {...props} />
                                              }}
                                            >
                                              {streamingText}
                                            </ReactMarkdown>
                                        )}
                                    </Box>
                                }
                            />
                        </ListItem>
                    )}
                    {loading && !streamingText && <LinearProgress color="secondary" />}
                    <div ref={messagesEndRef} />
                </List>
            </Paper>

            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <input
                    accept="image/*,video/*,application/pdf,text/plain"
                    style={{ display: 'none' }}
                    id="raised-button-file"
                    type="file"
                    multiple
                    onChange={handleFileChange}
                />
                <label htmlFor="raised-button-file">
                    <IconButton color="primary" aria-label="upload picture" component="span">
                        <AttachFileIcon />
                    </IconButton>
                </label>
                {files.length > 0 && (
                    <Box sx={{ mr: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap', maxWidth: '200px' }}>
                        {files.map((f, i) => (
                            <Typography key={i} variant="caption" sx={{ bgcolor: 'rgba(255,255,255,0.1)', px: 0.5, borderRadius: 1 }}>
                                {f.name}
                            </Typography>
                        ))}
                    </Box>
                )}
                <TextField
                    fullWidth
                    variant="outlined"
                    placeholder={selectedPersonality.prompt_question}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                            handleSendMessage();
                        }
                    }}
                    sx={{ 
                        mr: 1, 
                        bgcolor: 'background.paper',
                        '& .MuiOutlinedInput-root': {
                            height: 56
                        }
                    }}
                />
                <Button 
                    variant="contained" 
                    onClick={handleSendMessage} 
                    disabled={loading && !streamingText}
                    sx={{ 
                        height: 56,
                        minWidth: '120px',
                        pl: 3,
                        bgcolor: '#000000', 
                        color: '#fff',
                        border: '2px solid #000000',
                        '&:hover': {
                            bgcolor: '#111',
                            borderColor: 'secondary.main'
                        },
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1
                    }}
                >
                    Send
                    <Box 
                        component="img" 
                        src="/portal_gun_trans.png" 
                        sx={{ height: 40 }} 
                        data-testid="portal-gun-icon"
                    />
                </Button>
            </Box>

            {/* Swirling Portal Animation Overlay */}
            <PortalAnimation show={showPortal} />

            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
                <Link href="/privacy" passHref legacyBehavior>
                    <Typography component="a" variant="caption" color="primary" sx={{ cursor: 'pointer', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
                        Privacy Policy
                    </Typography>
                </Link>
            </Box>
        </Box>
    );
}
