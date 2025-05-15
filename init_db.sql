CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    username TEXT,
    name TEXT,
    email TEXT,
    rating INTEGER,
    category TEXT,
    product TEXT,
    comments TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for login test results
CREATE TABLE IF NOT EXISTS test_results (
    id SERIAL PRIMARY KEY,
    username TEXT,
    expected TEXT,
    actual TEXT,
    result TEXT,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    batch_id TEXT
);

-- Table for feedback form test results
CREATE TABLE IF NOT EXISTS form_test_results (
    id SERIAL PRIMARY KEY,
    username TEXT,
    name TEXT,
    email TEXT,
    rating INT,
    category TEXT,
    product TEXT,
    comments TEXT,
    expected TEXT,
    actual TEXT,
    result TEXT,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    batch_id TEXT
);