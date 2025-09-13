-- DDL_CREATE_V2.sql (aggiornato)
DROP DATABASE IF EXISTS travel_db;
CREATE DATABASE travel_db;

-- \c travel_db

CREATE TABLE users (
  user_id VARCHAR(50) PRIMARY KEY,
  consent_flags JSONB DEFAULT '{"ai_processing": false}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE travel_requests (
  travel_id VARCHAR(50) PRIMARY KEY,
  user_id VARCHAR(50) REFERENCES users(user_id),
  origin VARCHAR(100),  -- Allineato
  destination VARCHAR(100),  -- Allineato
  start_date VARCHAR(10),  -- Allineato
  end_date VARCHAR(10),  -- Allineato
  interests JSONB DEFAULT '[]'::jsonb,  -- Nuovo
  year_season_or_month VARCHAR(50),
  additional_notes TEXT,
  structured_output JSONB DEFAULT '{}'::jsonb,
  raw_llm_response TEXT,  -- Nuovo per raw Langchain
  messages JSONB DEFAULT '[]'::jsonb,
  current_llm_session_id VARCHAR(36),
  current_llm_model VARCHAR(200),
  current_llm_agent VARCHAR(200),
  status VARCHAR(20) DEFAULT 'draft',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE llm_sessions (
  session_id VARCHAR(36) PRIMARY KEY,
  travel_id VARCHAR(50) REFERENCES travel_requests(travel_id) ON DELETE CASCADE,
  model VARCHAR(200) NOT NULL,
  agent VARCHAR(200),
  session_conversation_id VARCHAR(200),
  started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  ended_at TIMESTAMP WITH TIME ZONE,
  metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE moderation_logs (
  log_id SERIAL PRIMARY KEY,
  user_id VARCHAR(50) REFERENCES users(user_id),
  action VARCHAR(100),
  details TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE personal_profiles (
  user_id VARCHAR(50) PRIMARY KEY REFERENCES users(user_id),
  name VARCHAR(100),  -- Nuovo
  age INTEGER,  -- Nuovo
  preferences JSONB DEFAULT '[]'::jsonb,  -- Allineato a list
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE travel_responses (  -- Nuova
  response_id VARCHAR(50) PRIMARY KEY,
  travel_id VARCHAR(50) REFERENCES travel_requests(travel_id) ON DELETE CASCADE,
  itinerary JSONB DEFAULT '[]'::jsonb,
  hotels JSONB DEFAULT '[]'::jsonb,
  transport JSONB DEFAULT '[]'::jsonb,
  events JSONB DEFAULT '[]'::jsonb,
  raw_llm_response TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes per efficienza
CREATE INDEX IF NOT EXISTS idx_travel_structured_output ON travel_requests USING GIN (structured_output);
CREATE INDEX IF NOT EXISTS idx_travel_messages ON travel_requests USING GIN (messages);
CREATE INDEX IF NOT EXISTS idx_travel_interests ON travel_requests USING GIN (interests);
CREATE INDEX IF NOT EXISTS idx_profile_preferences ON personal_profiles USING GIN (preferences);
CREATE INDEX IF NOT EXISTS idx_response_itinerary ON travel_responses USING GIN (itinerary);