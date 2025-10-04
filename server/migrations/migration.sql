CREATE TABLE IF NOT EXISTS logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  event ENUM('question', 'error') NOT NULL,
  question TEXT NULL,
  answer TEXT NULL,
  question_timestamp DATETIME NULL,
  answer_timestamp DATETIME NULL,
  error_timestamp DATETIME NULL,
  error_message TEXT NULL
);
