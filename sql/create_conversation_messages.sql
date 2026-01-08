-- Create messages table (row-per-message)
CREATE TABLE IF NOT EXISTS public.conversation_messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  conversation_id uuid NOT NULL,
  role text NOT NULL,
  message text NOT NULL,
  first_name text,
  timestamp timestamptz NOT NULL DEFAULT now()
);

-- Indexes to speed lookups
CREATE INDEX IF NOT EXISTS idx_convmsg_user_conv ON public.conversation_messages (user_id, conversation_id);
CREATE INDEX IF NOT EXISTS idx_convmsg_conv_time ON public.conversation_messages (conversation_id, timestamp);

-- Enable RLS and policies for messages table
ALTER TABLE IF EXISTS public.conversation_messages ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "messages_owner_select" ON public.conversation_messages;
CREATE POLICY "messages_owner_select" ON public.conversation_messages
  FOR SELECT TO authenticated
  USING ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "messages_owner_insert" ON public.conversation_messages;
CREATE POLICY "messages_owner_insert" ON public.conversation_messages
  FOR INSERT TO authenticated
  WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "messages_owner_update" ON public.conversation_messages;
CREATE POLICY "messages_owner_update" ON public.conversation_messages
  FOR UPDATE TO authenticated
  USING ((SELECT auth.uid()) = user_id)
  WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "messages_owner_delete" ON public.conversation_messages;
CREATE POLICY "messages_owner_delete" ON public.conversation_messages
  FOR DELETE TO authenticated
  USING ((SELECT auth.uid()) = user_id);

GRANT SELECT, INSERT, UPDATE, DELETE ON public.conversation_messages TO authenticated;
