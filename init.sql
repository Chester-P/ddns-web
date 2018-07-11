CREATE TABLE user(
    uid         INTEGER     PRIMARY KEY AUTOINCREMENT,
    username    TEXT        NOT NULL,
    name        TEXT        NOT NULL,
    email       TEXT        NOT NULL,
    password    TEXT        NOT NULL
);

CREATE TABLE zone(
    zone_id     INTEGER     PRIMARY KEY AUTOINCREMENT,
    created_by  INTEGER     REFERENCES user(uid),
    name        TEXT        NOT NULL
);

CREATE TABLE record(
    record_id   INTEGER     PRIMARY KEY AUTOINCREMENT,
    SOA_serial  INTEGER     DEFAULT 0,
    FQDN        TEXT        UNIQUE NOT NULL,
    TTL         INTEGER     DEFAULT 600,
    type        TEXT        NOT NULL,
    value       TEXT        NOT NULL,
    create_time DATETIME    DEFAULT CURRENT_TIMESTAMP,
    created_by  INTEGER     REFERENCES user(uid),
    zone        INTEGER     REFERENCES zone(zone_id)
);

CREATE TABLE privilege(
    user        INTEGER,
    zone        INTEGER,
    PRIMARY KEY(user, zone),
    FOREIGN KEY(user) REFERENCES user(uid),
    FOREIGN KEY(zone) REFERENCES zone(zone_id)
);

/*
Remember to use "PRAGMA foreign_keys = ON;"
to enforce foreign key constraint
*/
