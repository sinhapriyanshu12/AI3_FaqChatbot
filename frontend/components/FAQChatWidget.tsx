type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
};

export function FAQChatWidget() {
  return (
    <div>
      <button type="button">Chat</button>
      <div>Implement floating widget UI here.</div>
    </div>
  );
}
