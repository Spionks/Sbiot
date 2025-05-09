/*
DROP TABLE IF EXISTS records;
DROP TABLE IF EXISTS spin_records;
DROP TABLE IF EXISTS timeouts;
*/

CREATE TABLE IF NOT EXISTS records(
    username TEXT,
    record_name TEXT,
    val TEXT
);

CREATE TABLE IF NOT EXISTS rsn_discord_names(
    rsn TEXT,
    discord_name TEXT
);

CREATE TABLE IF NOT EXISTS maffy_tasks(
    task TEXT,
    added TEXT,
    rolled TEXT,
    completed TEXT
);