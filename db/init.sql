-- Initialize database schema for predictions

CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    modality VARCHAR(50) NOT NULL,
    input_data TEXT NOT NULL,
    prediction TEXT NOT NULL,
    latency FLOAT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX idx_predictions_modality ON predictions(modality);
CREATE INDEX idx_predictions_created_at ON predictions(created_at DESC);

-- Create table for request logs
CREATE TABLE IF NOT EXISTS request_logs (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    latency FLOAT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_request_logs_endpoint ON request_logs(endpoint);
CREATE INDEX idx_request_logs_created_at ON request_logs(created_at DESC);
