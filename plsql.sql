SELECT 'I return data!' AS msg;
DO $$ BEGIN RAISE NOTICE 'But I only log to output!';
END $$;
DO $$ BEGIN RAISE EXCEPTION 'I raise an exception with a hint!' USING HINT = 'This is a hint for the exception.';
END $$;