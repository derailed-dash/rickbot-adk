export interface Personality {
    name: string;
    description: string;
    avatar: string;
    title: string;
    overview: string;
    welcome: string;
    prompt_question: string;
}

export interface Message {
    id: string;
    text: string;
    sender: 'user' | 'bot';
    personality?: string;
    attachments?: any[];
}
