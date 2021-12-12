-- Close All connections first
SELECT process
FROM stv_sessions
WHERE stv_sessions.db_name = 'tha';

SELECT pg_terminate_backend(<PID>);

-- Done by Terraform

DROP DATABASE IF EXISTS tha;
DROP USER IF EXISTS tha_admin;