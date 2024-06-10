CREATE TABLE public.Users (
    id VARCHAR(255) PRIMARY KEY,
    display_name VARCHAR(255) NOT NULL,
    followers INTEGER
);

CREATE TABLE public.Artists (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    genres TEXT[],
    followers INTEGER,
    type VARCHAR(50)
);

CREATE TABLE public.Shows (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    publisher VARCHAR(255),
    total_episodes INTEGER
);

CREATE TABLE public.Audiobooks (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    authors TEXT[],
    narrators TEXT[],
    publisher VARCHAR(255),
    release_date DATE,
    total_chapters INTEGER
);

CREATE TABLE public.Albums (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    release_date DATE,
    total_tracks INTEGER,
    artist_id VARCHAR(255) REFERENCES public.Artists(id),
    album_type VARCHAR(50)
);

CREATE TABLE public.Categories (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE public.Genres (
    name VARCHAR(255) PRIMARY KEY
);

CREATE TABLE public.Markets (
    country VARCHAR(255) PRIMARY KEY
);

CREATE TABLE public.Playlists (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) REFERENCES public.Users(id),
    description TEXT,
    public BOOLEAN
);

CREATE TABLE public.Tracks (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    duration_ms INTEGER,
    track_number INTEGER,
    album_id VARCHAR(255) REFERENCES public.Albums(id),
    artist_id VARCHAR(255) REFERENCES public.Artists(id)
);

CREATE TABLE public.Chapters (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    duration_ms INTEGER,
    audiobook_id VARCHAR(255) REFERENCES public.Audiobooks(id)
);

CREATE TABLE public.Episodes (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    duration_ms INTEGER,
    release_date DATE,
    show_id VARCHAR(255) REFERENCES public.Shows(id)
);

CREATE TABLE public.PlaylistTracks (
    playlist_id VARCHAR(255) REFERENCES public.Playlists(id),
    track_id VARCHAR(255) REFERENCES public.Tracks(id),
    PRIMARY KEY (playlist_id, track_id)
);
