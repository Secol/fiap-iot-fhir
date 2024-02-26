-- Criação de usuário
-- CREATE USER publisher WITH PASSWORD 'publisher';

-- Criação da tabela, se não existir
CREATE TABLE IF NOT EXISTS patient_heart_beat_records (
    id_patient INT,
    heart_beat INT,
    record_time TIMESTAMP
);