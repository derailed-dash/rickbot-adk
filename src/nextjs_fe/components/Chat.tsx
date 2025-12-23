import React, { useState, useEffect, useRef } from 'react';
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
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

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
}

const initialPersonalities: Personality[] = [
    { name: 'Rick', description: 'Rick Sanchez', avatar: '/avatars/rick.png' }
];

export default function Chat() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [personalities, setPersonalities] = useState<Personality[]>(initialPersonalities);
    const [inputValue, setInputValue] = useState('');
    const [selectedPersonality, setSelectedPersonality] = useState('Rick');
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [file, setFile] = useState<File | null>(null);
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
            try {
                const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/personas`);
                if (response.data && Array.isArray(response.data)) {
                    setPersonalities(response.data);
                }
            } catch (error) {
                console.error("Failed to fetch personalities:", error);
            }
        };

        fetchPersonalities();
    }, []);



    const handleSendMessage = async () => {
        if (!inputValue.trim() && !file) return;

        const newMessage: Message = {
            id: Date.now().toString(),
            text: inputValue,
            sender: 'user',
            attachments: file ? [file] : []
        };

        setMessages(prev => [...prev, newMessage]);
        setInputValue('');
        setFile(null);
        setLoading(true);
        setStreamingText('');

        try {
            const formData = new FormData();
            formData.append('prompt', newMessage.text);
            formData.append('personality', selectedPersonality);
            if (sessionId) {
                formData.append('session_id', sessionId);
            }
            if (file) {
                formData.append('file', file);
            }

            // Streaming implementation
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/chat_stream`, {
                method: 'POST',
                body: formData,
            });

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
                            if (data.chunk) {
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
                personality: selectedPersonality
            };
            setMessages(prev => [...prev, botMessage]);
            setStreamingText('');

        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: "Sorry, I encountered an error.",
                sender: 'bot',
                personality: selectedPersonality
            };
             setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files[0]) {
            setFile(event.target.files[0]);
        }
    };

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
                <Typography variant="h4" color="primary">Rickbot ADK</Typography>
                <FormControl sx={{ minWidth: 120 }}>
                    <InputLabel id="personality-select-label">Personality</InputLabel>
                    <Select
                        labelId="personality-select-label"
                        value={selectedPersonality}
                        label="Personality"
                        onChange={(e) => setSelectedPersonality(e.target.value)}
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
                    {loading && streamingText && (
                         <ListItem alignItems="flex-start">
                            <ListItemAvatar>
                                <Avatar src={`/avatars/${selectedPersonality.toLowerCase()}.png`} />
                            </ListItemAvatar>
                            <ListItemText
                                primary={
                                    <Box component="span" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                                        {selectedPersonality}
                                    </Box>
                                }
                                secondary={
                                    <Box component="span" sx={{ color: 'text.primary' }}>
                                        <ReactMarkdown
                                          components={{
                                            p: ({node, ...props}) => <span {...props} />
                                          }}
                                        >
                                          {streamingText}
                                        </ReactMarkdown>
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
                    accept="image/*,application/pdf,text/plain"
                    style={{ display: 'none' }}
                    id="raised-button-file"
                    type="file"
                    onChange={handleFileChange}
                />
                <label htmlFor="raised-button-file">
                    <IconButton color="primary" aria-label="upload picture" component="span">
                        <AttachFileIcon />
                    </IconButton>
                </label>
                {file && <Typography variant="caption" sx={{ mr: 1 }}>{file.name}</Typography>}
                <TextField
                    fullWidth
                    variant="outlined"
                    placeholder="Type a message..."
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
        </Box>
    );
}
