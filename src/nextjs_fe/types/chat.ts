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

export interface ToolCall {
    name: string;
    args: Record<string, any>;
}

export interface ToolResponse {
    name: string;
}

export interface AgentTransfer {
    target_agent: string;
}
