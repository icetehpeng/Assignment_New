-- ============================================================================
-- Smart Home Elderly Care System - Complete Database Setup
-- ============================================================================
-- This SQL file sets up the entire database with all tables needed for:
-- - Core system (users, activity, reminders, messages)
-- - Health tracking (vital signs, medications, mood, nutrition)
-- - Safety features (emergency contacts, SOS, geofencing)
-- - Smart home (devices, routines)
-- - Privacy & security (access permissions, access logs)
-- - Error handling & recovery
-- - Fall detection (NEW)
-- ============================================================================

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS elderly_care_system;
USE elderly_care_system;

-- ============================================================================
-- CORE SYSTEM TABLES
-- ============================================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Activity log table
CREATE TABLE IF NOT EXISTS activity_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    activity VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reminders table
CREATE TABLE IF NOT EXISTS reminders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    title VARCHAR(100),
    message TEXT,
    trigger_time DATETIME,
    repeat_type VARCHAR(20),
    audio_data LONGBLOB,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Messages table for chat
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender VARCHAR(50),
    receiver VARCHAR(50),
    content TEXT,
    audio_data LONGBLOB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sender (sender),
    INDEX idx_receiver (receiver),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- HEALTH TRACKING TABLES
-- ============================================================================

-- Vital signs table
CREATE TABLE IF NOT EXISTS vital_signs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    vital_type VARCHAR(50),
    value FLOAT,
    unit VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_vital_type (vital_type),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Medications table
CREATE TABLE IF NOT EXISTS medications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    name VARCHAR(100),
    dosage VARCHAR(50),
    frequency VARCHAR(50),
    start_date DATE,
    end_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Medication logs table
CREATE TABLE IF NOT EXISTS medication_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    medication_name VARCHAR(100),
    taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_taken_at (taken_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Meals table
CREATE TABLE IF NOT EXISTS meals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    meal_name VARCHAR(100),
    food_items TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Water logs table
CREATE TABLE IF NOT EXISTS water_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    amount_ml INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Mood logs table
CREATE TABLE IF NOT EXISTS mood_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    mood_emoji VARCHAR(10),
    mood_text VARCHAR(50),
    notes TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Depression screenings table
CREATE TABLE IF NOT EXISTS depression_screenings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    phq9_score INT,
    severity VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cognitive activities table
CREATE TABLE IF NOT EXISTS cognitive_activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    game_name VARCHAR(100),
    score INT,
    duration_minutes INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Activity logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    activity_type VARCHAR(50),
    duration_minutes INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_activity_type (activity_type),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- SAFETY & EMERGENCY TABLES
-- ============================================================================

-- Emergency contacts table
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    contact_name VARCHAR(100),
    phone_number VARCHAR(20),
    priority INT,
    relation VARCHAR(50),
    alert_on_fall BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_priority (priority)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- SOS logs table
CREATE TABLE IF NOT EXISTS sos_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location_lat FLOAT,
    location_lon FLOAT,
    alert_type VARCHAR(50) DEFAULT 'MANUAL_SOS',
    INDEX idx_username (username),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Safe zones table
CREATE TABLE IF NOT EXISTS safe_zones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    zone_name VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    radius_meters INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Location logs table
CREATE TABLE IF NOT EXISTS location_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    latitude FLOAT,
    longitude FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- FALL DETECTION TABLES (NEW)
-- ============================================================================

-- Fall incidents table
CREATE TABLE IF NOT EXISTS fall_incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    timestamp DATETIME,
    severity VARCHAR(50),
    confidence FLOAT,
    immobility_duration FLOAT,
    location_lat FLOAT,
    location_lon FLOAT,
    image_path VARCHAR(255),
    alert_sent BOOLEAN DEFAULT FALSE,
    recovery_detected BOOLEAN DEFAULT FALSE,
    recovery_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_timestamp (timestamp),
    INDEX idx_severity (severity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Fall statistics table
CREATE TABLE IF NOT EXISTS fall_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    falls_per_week INT,
    average_recovery_time FLOAT,
    common_time_of_day VARCHAR(50),
    common_location VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Fall logs table (for detailed logging)
CREATE TABLE IF NOT EXISTS fall_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    severity VARCHAR(50),
    confidence FLOAT,
    timestamp DATETIME,
    action VARCHAR(100),
    INDEX idx_username (username),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- SMART HOME TABLES
-- ============================================================================

-- Smart devices table
CREATE TABLE IF NOT EXISTS smart_devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(50),
    device_name VARCHAR(100),
    device_type VARCHAR(50),
    ip_address VARCHAR(50),
    port INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_device_id (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Device logs table
CREATE TABLE IF NOT EXISTS device_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(50),
    action TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_device_id (device_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Routines table
CREATE TABLE IF NOT EXISTS routines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    routine_name VARCHAR(100),
    trigger_condition TEXT,
    actions TEXT,
    enabled BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_enabled (enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- PRIVACY & SECURITY TABLES
-- ============================================================================

-- Access permissions table
CREATE TABLE IF NOT EXISTS access_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    caregiver VARCHAR(50),
    permissions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_caregiver (caregiver)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Time-based access table
CREATE TABLE IF NOT EXISTS time_based_access (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    caregiver VARCHAR(50),
    start_time TIME,
    end_time TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Access logs table
CREATE TABLE IF NOT EXISTS access_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    caregiver VARCHAR(50),
    resource_type VARCHAR(50),
    action VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_caregiver (caregiver),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- ERROR HANDLING & RECOVERY TABLES
-- ============================================================================

-- Error logs table
CREATE TABLE IF NOT EXISTS error_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    error_id VARCHAR(50) UNIQUE,
    error_type VARCHAR(100),
    message TEXT,
    severity VARCHAR(20),
    username VARCHAR(50),
    context JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_error_type (error_type),
    INDEX idx_timestamp (timestamp),
    INDEX idx_severity (severity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Recovery logs table
CREATE TABLE IF NOT EXISTS recovery_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    error_id VARCHAR(50),
    recovery_action TEXT,
    success BOOLEAN,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_error_id (error_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- USER PREFERENCES & SETTINGS TABLES
-- ============================================================================

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    theme VARCHAR(50) DEFAULT 'dark',
    language VARCHAR(10) DEFAULT 'en',
    dashboard_layout JSON,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Activities table (for activity tracking)
CREATE TABLE IF NOT EXISTS activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    activity_type VARCHAR(50),
    duration_minutes INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- OFFLINE SYNC TABLES
-- ============================================================================

-- Offline sync queue table
CREATE TABLE IF NOT EXISTS offline_sync_queue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    operation VARCHAR(50),
    table_name VARCHAR(100),
    record_id INT,
    data JSON,
    synced BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synced_at TIMESTAMP NULL,
    INDEX idx_username (username),
    INDEX idx_synced (synced)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- ANALYTICS & REPORTING TABLES
-- ============================================================================

-- Daily health summary table
CREATE TABLE IF NOT EXISTS daily_health_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    date DATE,
    avg_heart_rate FLOAT,
    avg_blood_pressure VARCHAR(20),
    avg_temperature FLOAT,
    avg_blood_oxygen FLOAT,
    total_steps INT,
    total_water_ml INT,
    mood_average FLOAT,
    sleep_hours FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Weekly health report table
CREATE TABLE IF NOT EXISTS weekly_health_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    week_start DATE,
    week_end DATE,
    total_falls INT,
    critical_falls INT,
    average_activity_level VARCHAR(50),
    medication_adherence FLOAT,
    mood_trend VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_week_start (week_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- Insert sample user (optional)
-- INSERT INTO users (username, password_hash) VALUES ('test_user', 'test_password');

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for recent vital signs
CREATE OR REPLACE VIEW recent_vital_signs AS
SELECT 
    username,
    vital_type,
    value,
    unit,
    timestamp
FROM vital_signs
WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY timestamp DESC;

-- View for active medications
CREATE OR REPLACE VIEW active_medications AS
SELECT 
    username,
    name,
    dosage,
    frequency,
    start_date,
    end_date
FROM medications
WHERE end_date IS NULL OR end_date >= CURDATE()
ORDER BY username, name;

-- View for recent falls
CREATE OR REPLACE VIEW recent_falls AS
SELECT 
    username,
    timestamp,
    severity,
    confidence,
    immobility_duration,
    recovery_detected
FROM fall_incidents
WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY timestamp DESC;

-- View for user activity summary
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT 
    username,
    COUNT(*) as total_activities,
    SUM(duration_minutes) as total_duration,
    AVG(duration_minutes) as avg_duration,
    MAX(timestamp) as last_activity
FROM activity_logs
GROUP BY username;

-- ============================================================================
-- STORED PROCEDURES
-- ============================================================================

-- Procedure to get user health summary
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS get_user_health_summary(IN p_username VARCHAR(50))
BEGIN
    SELECT 
        (SELECT COUNT(*) FROM vital_signs WHERE username = p_username) as vital_signs_count,
        (SELECT COUNT(*) FROM medications WHERE username = p_username AND end_date IS NULL) as active_medications,
        (SELECT COUNT(*) FROM fall_incidents WHERE username = p_username AND DATE(timestamp) = CURDATE()) as falls_today,
        (SELECT AVG(value) FROM vital_signs WHERE username = p_username AND vital_type = 'heart_rate' AND timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)) as avg_heart_rate,
        (SELECT COUNT(*) FROM mood_logs WHERE username = p_username AND DATE(timestamp) = CURDATE()) as mood_entries_today;
END //
DELIMITER ;

-- Procedure to log fall incident
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS log_fall_incident(
    IN p_username VARCHAR(50),
    IN p_severity VARCHAR(50),
    IN p_confidence FLOAT,
    IN p_immobility_duration FLOAT,
    IN p_location_lat FLOAT,
    IN p_location_lon FLOAT
)
BEGIN
    INSERT INTO fall_incidents (
        username,
        timestamp,
        severity,
        confidence,
        immobility_duration,
        location_lat,
        location_lon,
        alert_sent
    ) VALUES (
        p_username,
        NOW(),
        p_severity,
        p_confidence,
        p_immobility_duration,
        p_location_lat,
        p_location_lon,
        TRUE
    );
END //
DELIMITER ;

-- Procedure to get fall statistics
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS get_fall_statistics(IN p_username VARCHAR(50), IN p_days INT)
BEGIN
    SELECT 
        COUNT(*) as total_falls,
        SUM(CASE WHEN severity = 'CRITICAL_FALL' THEN 1 ELSE 0 END) as critical_falls,
        SUM(CASE WHEN severity = 'CONFIRMED_FALL' THEN 1 ELSE 0 END) as confirmed_falls,
        AVG(confidence) as avg_confidence,
        AVG(immobility_duration) as avg_immobility_duration,
        SUM(CASE WHEN recovery_detected = TRUE THEN 1 ELSE 0 END) as recovered_falls
    FROM fall_incidents
    WHERE username = p_username 
    AND timestamp >= DATE_SUB(NOW(), INTERVAL p_days DAY);
END //
DELIMITER ;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Note: Composite indexes are already defined within table definitions
-- Additional indexes are not needed as they are already created

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

-- Display completion status
SELECT '✅ Database setup complete!' as status;
SELECT COUNT(*) as total_tables FROM information_schema.tables WHERE table_schema = 'elderly_care_system';

-- ============================================================================
-- END OF SETUP SCRIPT
-- ============================================================================
