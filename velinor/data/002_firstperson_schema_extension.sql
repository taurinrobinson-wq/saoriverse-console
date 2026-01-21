-- ============================================================================
-- FirstPerson Schema Extension
-- Adds anchor tracking, theme frequency analysis, and temporal patterns
-- Extends conversations table and creates new tables for memory persistence
-- ============================================================================
--
-- New Columns Added to conversations table:
--   - anchor: text - Short memorable phrase capturing emotional essence
--   - summary: text - Brief 1-2 sentence summary of conversation
--   - primary_theme: text - Most detected emotional theme
--   - clarifiers_used: text[] - Array of clarifying prompts employed
--   - detected_affects: jsonb - Structured affect data {valence, arousal, tone}
--   - detected_time_patterns: jsonb - Temporal information {time_of_day, frequency_pattern}
--   - user_feedback: jsonb - Feedback signals {helpful, resonant, unexpected}
--   - anchor_salience: numeric - Relevance score for future retrieval (0-1)
--
-- New Tables:
--   - theme_anchors - Persistent storage of emotional themes with frequency
--   - theme_history - Time-series tracking of theme emergence
--   - temporal_patterns - Time-of-day and day-of-week patterns
-- ============================================================================

-- ============================================================================
-- ALTER conversations TABLE - Add FirstPerson columns
-- ============================================================================

-- Add new columns for FirstPerson if they don't already exist
-- Using conditional creation to be idempotent

ALTER TABLE public.conversations 
ADD COLUMN IF NOT EXISTS anchor text,
ADD COLUMN IF NOT EXISTS summary text,
ADD COLUMN IF NOT EXISTS primary_theme text,
ADD COLUMN IF NOT EXISTS clarifiers_used text[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS detected_affects jsonb DEFAULT '{"valence": null, "arousal": null, "tone": null}',
ADD COLUMN IF NOT EXISTS detected_time_patterns jsonb DEFAULT '{"time_of_day": null, "frequency_pattern": null, "day_of_week": null}',
ADD COLUMN IF NOT EXISTS user_feedback jsonb DEFAULT '{"helpful": null, "resonant": null, "unexpected": null, "ratings": []}',
ADD COLUMN IF NOT EXISTS anchor_salience numeric DEFAULT 0.5 CHECK (anchor_salience >= 0 AND anchor_salience <= 1);

-- ============================================================================
-- CREATE theme_anchors TABLE
-- Persistent storage of detected themes with frequency and metadata
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.theme_anchors (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id text NOT NULL,
    theme text NOT NULL,
    anchor text NOT NULL,
    frequency integer DEFAULT 1,
    first_detected_at timestamptz DEFAULT now(),
    last_detected_at timestamptz DEFAULT now(),
    context jsonb DEFAULT '{}', -- Store context of first detection
    confidence numeric DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
    status text DEFAULT 'active', -- 'active', 'resolved', 'recurring'
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Create indexes for efficient theme lookups
CREATE INDEX IF NOT EXISTS idx_theme_anchors_user_id 
ON public.theme_anchors (user_id);

CREATE INDEX IF NOT EXISTS idx_theme_anchors_theme 
ON public.theme_anchors (theme);

CREATE INDEX IF NOT EXISTS idx_theme_anchors_user_theme 
ON public.theme_anchors (user_id, theme);

CREATE INDEX IF NOT EXISTS idx_theme_anchors_last_detected_at 
ON public.theme_anchors (last_detected_at DESC);

CREATE INDEX IF NOT EXISTS idx_theme_anchors_frequency 
ON public.theme_anchors (frequency DESC);

-- Create unique constraint to prevent duplicate anchors per user per theme
CREATE UNIQUE INDEX IF NOT EXISTS idx_theme_anchors_user_theme_anchor 
ON public.theme_anchors (user_id, theme, anchor)
WHERE status = 'active';

-- ============================================================================
-- CREATE theme_history TABLE
-- Time-series tracking of theme emergence for pattern analysis
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.theme_history (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id text NOT NULL,
    conversation_id text,
    theme text NOT NULL,
    frequency_at_time integer DEFAULT 1, -- How many times theme appeared in this session
    detected_at timestamptz DEFAULT now(),
    context jsonb DEFAULT '{}', -- Store brief context (first few words of message)
    affect_state jsonb DEFAULT '{"valence": null, "arousal": null}',
    time_of_day text, -- 'morning', 'afternoon', 'evening', 'night'
    day_of_week text -- 'Monday', 'Tuesday', etc.
);

-- Create indexes for time-series queries
CREATE INDEX IF NOT EXISTS idx_theme_history_user_id 
ON public.theme_history (user_id);

CREATE INDEX IF NOT EXISTS idx_theme_history_theme 
ON public.theme_history (theme);

CREATE INDEX IF NOT EXISTS idx_theme_history_detected_at 
ON public.theme_history (detected_at DESC);

CREATE INDEX IF NOT EXISTS idx_theme_history_user_theme_time 
ON public.theme_history (user_id, theme, detected_at DESC);

-- Composite index for efficient daily pattern queries
CREATE INDEX IF NOT EXISTS idx_theme_history_user_time_of_day 
ON public.theme_history (user_id, time_of_day);

CREATE INDEX IF NOT EXISTS idx_theme_history_user_day_of_week 
ON public.theme_history (user_id, day_of_week);

-- ============================================================================
-- CREATE temporal_patterns TABLE
-- Aggregated time-of-day and day-of-week patterns for intelligent timing
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.temporal_patterns (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id text NOT NULL,
    theme text NOT NULL,
    time_of_day text NOT NULL, -- 'morning', 'afternoon', 'evening', 'night'
    day_of_week text, -- NULL means pattern holds across all days
    frequency integer DEFAULT 1,
    avg_intensity numeric DEFAULT 0.5, -- Average affect arousal during this pattern
    last_observed_at timestamptz DEFAULT now(),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Create indexes for efficient pattern lookup
CREATE INDEX IF NOT EXISTS idx_temporal_patterns_user_id 
ON public.temporal_patterns (user_id);

CREATE INDEX IF NOT EXISTS idx_temporal_patterns_theme 
ON public.temporal_patterns (theme);

CREATE INDEX IF NOT EXISTS idx_temporal_patterns_user_theme 
ON public.temporal_patterns (user_id, theme);

CREATE INDEX IF NOT EXISTS idx_temporal_patterns_time_of_day 
ON public.temporal_patterns (time_of_day);

CREATE INDEX IF NOT EXISTS idx_temporal_patterns_day_of_week 
ON public.temporal_patterns (day_of_week);

-- Create unique constraint per user/theme/time pattern
CREATE UNIQUE INDEX IF NOT EXISTS idx_temporal_patterns_unique 
ON public.temporal_patterns (user_id, theme, time_of_day, COALESCE(day_of_week, 'any'));

-- ============================================================================
-- Helper Functions for Theme Analysis
-- ============================================================================

-- Function to calculate time_of_day from timestamp
CREATE OR REPLACE FUNCTION get_time_of_day(ts timestamptz)
RETURNS text AS $$
DECLARE
    hour integer;
BEGIN
    hour := EXTRACT(HOUR FROM ts AT TIME ZONE 'UTC');
    
    CASE 
        WHEN hour >= 5 AND hour < 12 THEN RETURN 'morning';
        WHEN hour >= 12 AND hour < 17 THEN RETURN 'afternoon';
        WHEN hour >= 17 AND hour < 21 THEN RETURN 'evening';
        ELSE RETURN 'night';
    END CASE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to get day of week name
CREATE OR REPLACE FUNCTION get_day_of_week(ts timestamptz)
RETURNS text AS $$
BEGIN
    RETURN TO_CHAR(ts AT TIME ZONE 'UTC', 'Day');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- Sample Queries for Theme Analysis
-- ============================================================================
--
-- Query 1: Get theme frequency for a user (last 30 days)
--
-- SELECT theme, COUNT(*) as frequency, COUNT(DISTINCT DATE(detected_at)) as days_appeared
-- FROM public.theme_history
-- WHERE user_id = 'user_123' 
--   AND detected_at > now() - interval '30 days'
-- GROUP BY theme
-- ORDER BY frequency DESC;
--
--
-- Query 2: Get top themes for a specific time of day
--
-- SELECT theme, frequency, avg_intensity
-- FROM public.temporal_patterns
-- WHERE user_id = 'user_123'
--   AND time_of_day = 'evening'
-- ORDER BY frequency DESC
-- LIMIT 5;
--
--
-- Query 3: Get recent anchors for memory rehydration
--
-- SELECT anchor, theme, frequency, last_detected_at
-- FROM public.theme_anchors
-- WHERE user_id = 'user_123'
--   AND status = 'active'
-- ORDER BY last_detected_at DESC
-- LIMIT 20;
--
--
-- Query 4: Detect recurring patterns (same theme on same day/time)
--
-- SELECT theme, day_of_week, time_of_day, frequency, avg_intensity
-- FROM public.temporal_patterns
-- WHERE user_id = 'user_123'
--   AND frequency >= 3  -- Has appeared 3+ times at this specific time
--   AND avg_intensity > 0.6  -- With high emotional intensity
-- ORDER BY frequency DESC;
--
--
-- Query 5: Theme emergence timeline (for narrative analysis)
--
-- SELECT 
--     DATE(detected_at) as detection_date,
--     theme,
--     COUNT(*) as daily_frequency,
--     AVG(CAST((affect_state->>'arousal')::numeric AS numeric)) as avg_arousal
-- FROM public.theme_history
-- WHERE user_id = 'user_123'
--   AND detected_at > now() - interval '90 days'
-- GROUP BY DATE(detected_at), theme
-- ORDER BY detection_date DESC, daily_frequency DESC;
--
-- ============================================================================

-- Update trigger for theme_anchors
DROP TRIGGER IF EXISTS theme_anchors_update_updated_at ON public.theme_anchors;
CREATE TRIGGER theme_anchors_update_updated_at
BEFORE UPDATE ON public.theme_anchors
FOR EACH ROW
EXECUTE FUNCTION update_conversation_updated_at();

-- Update trigger for temporal_patterns
DROP TRIGGER IF EXISTS temporal_patterns_update_updated_at ON public.temporal_patterns;
CREATE TRIGGER temporal_patterns_update_updated_at
BEFORE UPDATE ON public.temporal_patterns
FOR EACH ROW
EXECUTE FUNCTION update_conversation_updated_at();

-- ============================================================================
-- SECURITY: Row Level Security (RLS) for FirstPerson Tables
-- ============================================================================
--
-- IMPORTANT: Enable RLS for all new FirstPerson tables:
--
-- ALTER TABLE public.theme_anchors ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.theme_history ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.temporal_patterns ENABLE ROW LEVEL SECURITY;
--
-- CREATE POLICY theme_anchors_user_isolation ON public.theme_anchors
--     FOR ALL USING (user_id = auth.uid()::text);
--
-- CREATE POLICY theme_history_user_isolation ON public.theme_history
--     FOR ALL USING (user_id = auth.uid()::text);
--
-- CREATE POLICY temporal_patterns_user_isolation ON public.temporal_patterns
--     FOR ALL USING (user_id = auth.uid()::text);
--
-- ============================================================================

COMMIT;
