// Type definitions for Deno edge functions

// Global Deno types
declare global {
  const Deno: {
    env: {
      get(key: string): string | undefined;
    };
    serve: (handler: (req: Request) => Promise<Response> | Response) => void;
  };
}

// Supabase client types
interface SupabaseClient {
  from(table: string): any;
}

// OpenAI types
interface OpenAI {
  chat: {
    completions: {
      create(options: any): Promise<any>;
    };
  };
}

// Request/Response types for edge functions
interface RequestHandler {
  (req: Request): Promise<Response> | Response;
}

// Common edge function types
interface GlyphData {
  id?: string;
  name: string;
  description?: string;
  response_layer?: string;
  depth?: number;
  [key: string]: any;
}

interface LearningData {
  timestamp: string;
  user_emotions: Record<string, string[]>;
  ai_patterns: Record<string, boolean>;
  key_phrases: string[];
  confidence: number;
}

export {
  SupabaseClient,
  OpenAI,
  RequestHandler,
  GlyphData,
  LearningData
};