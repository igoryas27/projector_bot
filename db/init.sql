CREATE TABLE IF NOT EXISTS public.users
(
    user_id bigint NOT NULL,
    full_name text COLLATE pg_catalog."default",
    username text COLLATE pg_catalog."default",
    phone_number text COLLATE pg_catalog."default",
    quests_completed integer DEFAULT 0,
    trophies_received integer DEFAULT 0,
    total_points integer DEFAULT 0,
    CONSTRAINT users_pkey PRIMARY KEY (user_id),
    CONSTRAINT unique_username UNIQUE (username)
)
