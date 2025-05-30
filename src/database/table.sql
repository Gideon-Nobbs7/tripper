CREATE TABLE IF NOT EXISTS trip(
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp
);

CREATE INDEX IF NOT EXISTS trip_id_idx ON trip(id);
CREATE INDEX IF NOT EXISTS trip_name_idx ON trip(name);


CREATE TABLE IF NOT EXISTS destination(
    id SERIAL PRIMARY KEY,
    location VARCHAR(50) NOT NULL,
    longitude FLOAT NOT NULL,
    lattitude FLOAT NOT NULL,
    distance_from_user FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
    trip_id INTEGER REFERENCES trip(id)
);

CREATE INDEX IF NOT EXISTS destination_id_idx ON destination(id);
CREATE INDEX IF NOT EXISTS destination_loc_idx ON destination(location);
