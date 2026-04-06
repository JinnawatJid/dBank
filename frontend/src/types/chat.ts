export interface Message {
  role: "user" | "assistant";
  content: string;
  tools_used?: string[];
}
