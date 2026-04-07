DO $$ BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'testuser') THEN
        CREATE USER testuser WITH PASSWORD 'testpass';
    ELSE
        ALTER USER testuser WITH PASSWORD 'testpass';
    END IF;
END $$;
