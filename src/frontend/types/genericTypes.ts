interface Vendor {
    name: string;
    vocation: string | null;
    number: string;
    keywords: string[];
    active: boolean;
}

interface Tenant {
    name: string | null;
    number: string;
    address: string | null;
}

interface Conversation {
    tenant: Tenant;
    vendor: Vendor | null;
    date_created: Date;
    is_active: boolean;
    assistant_messages: Message[]; // Assuming you have a Message interface
    vendor_messages: Message[]; // Assuming you have a Message interface
}

interface Message {
    sender_number: string;
    receiver_number: string;
    time_sent: Date;
    role: string; // You may want to make this an enum instead
    message_content: string;
    media_url: string | null;
    conversation: Conversation;
}

interface PhoneNumber {
    number: string;
    most_recent_conversation: Conversation | null;
    is_base_number: boolean;
}
