-- ============================================================
-- Supabase Migration: Add food_entries, supplements, vocabulary
-- Run this in the Supabase SQL editor (Dashboard > SQL Editor)
-- Safe to run multiple times (uses IF NOT EXISTS / DO blocks)
-- ============================================================


-- ── food_entries ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS food_entries (
    id          BIGSERIAL PRIMARY KEY,
    "Date"      TEXT NOT NULL,
    meal_type   TEXT NOT NULL,
    food_name   TEXT NOT NULL,
    calories    INTEGER NOT NULL DEFAULT 0,
    protein     REAL DEFAULT 0,
    carbs       REAL DEFAULT 0,
    fat         REAL DEFAULT 0,
    vitamin_a   REAL DEFAULT 0,
    vitamin_c   REAL DEFAULT 0,
    vitamin_d   REAL DEFAULT 0,
    calcium     REAL DEFAULT 0,
    iron        REAL DEFAULT 0,
    magnesium   REAL DEFAULT 0,
    zinc        REAL DEFAULT 0,
    potassium   REAL DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (disable for personal use, or set policy below)
ALTER TABLE food_entries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all" ON food_entries FOR ALL USING (true) WITH CHECK (true);


-- ── supplements ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS supplements (
    id               BIGSERIAL PRIMARY KEY,
    "Date"           TEXT NOT NULL,
    supplement_name  TEXT NOT NULL,
    dosage           REAL DEFAULT 0,
    unit             TEXT DEFAULT 'mg',
    taken            BOOLEAN DEFAULT false,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE ("Date", supplement_name)
);

ALTER TABLE supplements ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all" ON supplements FOR ALL USING (true) WITH CHECK (true);


-- ── vocabulary ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vocabulary (
    id               BIGSERIAL PRIMARY KEY,
    word             TEXT NOT NULL UNIQUE,
    cefr_level       TEXT,
    definition       TEXT,
    example_sentence TEXT,
    translation      TEXT,
    importance       INTEGER DEFAULT 3,
    mastery          INTEGER DEFAULT 4,
    category         TEXT,
    date_added       TEXT,
    last_reviewed    TEXT,
    times_reviewed   INTEGER DEFAULT 0,
    next_review_date TEXT
);

ALTER TABLE vocabulary ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all" ON vocabulary FOR ALL USING (true) WITH CHECK (true);


-- ── Patch existing food_entries if vitamin columns are missing ─
-- (Only needed if food_entries already existed without vitamins)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='food_entries' AND column_name='vitamin_a'
    ) THEN
        ALTER TABLE food_entries
            ADD COLUMN vitamin_a  REAL DEFAULT 0,
            ADD COLUMN vitamin_c  REAL DEFAULT 0,
            ADD COLUMN vitamin_d  REAL DEFAULT 0,
            ADD COLUMN calcium    REAL DEFAULT 0,
            ADD COLUMN iron       REAL DEFAULT 0,
            ADD COLUMN magnesium  REAL DEFAULT 0,
            ADD COLUMN zinc       REAL DEFAULT 0,
            ADD COLUMN potassium  REAL DEFAULT 0;
    END IF;
END $$;
