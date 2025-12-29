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
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    IconButton,
    LinearProgress
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import PlumbusIcon from './PlumbusIcon';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import AuthButton from './AuthButton';
import Link from 'next/link';

interface Message {
    id: string;
    text: string;
    sender: 'user' | 'bot';
    personality?: string;
    attachments?: any[];
}

interface Personality {
    name: string;
    description: string;
    avatar: string;
    title: string;
    overview: string;
    welcome: string;
    prompt_question: string;
}

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

export default function Chat() {
    const { data: session, status } = useSession()
    const [messages, setMessages] = useState<Message[]>([]);
    const [personalities, setPersonalities] = useState<Personality[]>(initialPersonalities);
    const [inputValue, setInputValue] = useState('');
    const [selectedPersonality, setSelectedPersonality] = useState<Personality>(initialPersonalities[0]);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [botAction, setBotAction] = useState<string | null>(null);
    const [files, setFiles] = useState<File[]>([]);
    const messagesEndRef = useRef<null | HTMLDivElement>(null);
    const [streamingText, setStreamingText] = useState('');

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, streamingText]);

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
                                setBotAction(`Using tool: ${data.tool_call.name}...`);
                            }
                            if (data.agent_transfer) {
                                setBotAction(`Transferring to agent: ${data.agent_transfer}...`);
                            }
                            if (data.chunk) {
                                setBotAction('Responding...');
                                accumulatedText += data.chunk;
                                setStreamingText(accumulatedText);
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

        } catch (error) {
            console.error('Error sending message:', error);
            setBotAction(null);
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
                backgroundImage: 'url(/avatars/rickbot-trans.png)',
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'center',
                backgroundSize: 'contain',
                backgroundColor: 'rgba(0,0,0,0.8)',
                backgroundBlendMode: 'darken',
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
            backgroundImage: 'url(/avatars/rickbot-trans.png)',
            backgroundRepeat: 'no-repeat',
            backgroundPosition: 'center',
            backgroundSize: 'contain',
            backgroundColor: 'rgba(0,0,0,0.8)',
            backgroundBlendMode: 'darken'
        }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h4" color="primary">Rickbot</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <IconButton color="secondary" onClick={handleClearChat} title="Start New Chat">
                        <PlumbusIcon />
                    </IconButton>
                    <AuthButton />
                    <FormControl sx={{ minWidth: 120 }}>
                        <InputLabel id="personality-select-label">Personality</InputLabel>
                        <Select
                            labelId="personality-select-label"
                            value={selectedPersonality.name}
                            label="Personality"
                            onChange={(e) => {
                                const newP = personalities.find(p => p.name === e.target.value);
                                if (newP) setSelectedPersonality(newP);
                            }}
                        >
                            {personalities.map((p) => (
                                <MenuItem key={p.name} value={p.name}>
                                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                        <Avatar src={p.avatar} sx={{ width: 24, height: 24, mr: 1 }} />
                                        {p.name}
                                    </Box>
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Box>
            </Box>

            {/* Persona Profile Area */}
            <Paper elevation={3} sx={{ p: 2, mb: 2, bgcolor: 'rgba(30,30,30,0.95)', borderLeft: '4px solid', borderColor: 'primary.main' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Avatar 
                        src={selectedPersonality.avatar} 
                        sx={{ width: 64, height: 64, border: '2px solid', borderColor: 'primary.main' }} 
                    />
                    <Box>
                        <Typography variant="h6" color="primary.main" sx={{ fontWeight: 'bold' }}>
                            {selectedPersonality.title}
                        </Typography>
                        <Typography variant="body2" color="text.primary" sx={{ mb: 0.5 }}>
                            {selectedPersonality.overview}
                        </Typography>
                        <Typography variant="caption" color="secondary.main" sx={{ fontStyle: 'italic' }}>
                            {selectedPersonality.welcome}
                        </Typography>
                    </Box>
                </Box>
            </Paper>

            <Paper elevation={3} sx={{ flexGrow: 1, overflow: 'auto', p: 2, mb: 2, bgcolor: 'rgba(30,30,30,0.9)' }}>
                <List>
                    {messages.map((msg) => (
                        <ListItem key={msg.id} alignItems="flex-start">
                            <ListItemAvatar>
                                <Avatar src={msg.sender === 'user' ? '/avatars/morty.png' : `/avatars/${msg.personality?.toLowerCase()}.png`} />
                            </ListItemAvatar>
                            <ListItemText
                                primary={
                                    <Box component="span" sx={{ fontWeight: 'bold', color: msg.sender === 'user' ? 'secondary.main' : 'primary.main' }}>
                                        {msg.sender === 'user' ? 'You' : msg.personality}
                                    </Box>
                                }
                                secondary={
                                    <Box component="span" sx={{ color: 'text.primary' }}>
                                        {msg.attachments && msg.attachments.length > 0 && (
                                            <Box sx={{ mb: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                                {msg.attachments.map((att, i) => {
                                                    if (!(att instanceof File)) return null;
                                                    const url = URL.createObjectURL(att);
                                                    if (att.type.startsWith('image/')) {
                                                        return <Box key={i} component="img" src={url} sx={{ maxWidth: '100%', maxHeight: '300px', borderRadius: 1, display: 'block' }} />;
                                                    } else if (att.type.startsWith('video/')) {
                                                        return <Box key={i} component="video" src={url} controls sx={{ maxWidth: '100%', maxHeight: '300px', borderRadius: 1, display: 'block' }} />;
                                                    } else {
                                                        return (
                                                            <Paper key={i} variant="outlined" sx={{ p: 1, display: 'flex', alignItems: 'center', gap: 1, bgcolor: 'rgba(255,255,255,0.05)' }}>
                                                                <AttachFileIcon fontSize="small" />
                                                                <Typography variant="caption">{att.name}</Typography>
                                                            </Paper>
                                                        );
                                                    }
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
                                        {botAction && (
                                            <Typography component="span" variant="caption" color="secondary" sx={{ display: 'block', mb: 1, fontStyle: 'italic' }}>
                                                {botAction}
                                            </Typography>
                                        )}
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
                    sx={{ mr: 1, bgcolor: 'background.paper' }}
                />
                <Button variant="contained" endIcon={<SendIcon />} onClick={handleSendMessage} disabled={loading && !streamingText}>
                    Send
                </Button>
            </Box>
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
