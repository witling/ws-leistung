-- https://stackoverflow.com/a/10267699/13401153
CREATE TABLE images (
    id CHAR(64),
    description TEXT,
    added_date DATE NOT NULL,
    taken_date DATE,
    height INT,
    width INT,
    content BYTEA NOT NULL,

    PRIMARY KEY(id)
);

CREATE TABLE thumbnails (
    id CHAR(64),
    content BYTEA NOT NULL,

    PRIMARY KEY(id),
    CONSTRAINT fk_image FOREIGN KEY(id) REFERENCES images(id)
);

CREATE TABLE metadata (
    id CHAR(64),
    key INT NOT NULL,
    value TEXT NOT NULL,

    PRIMARY KEY(id, key),
    CONSTRAINT fk_image FOREIGN KEY(id) REFERENCES images(id)
);

CREATE TABLE tags (
    id CHAR(64) NOT NULL,
    name VARCHAR(32) NOT NULL,

    PRIMARY KEY(id, name),
    CONSTRAINT fk_image FOREIGN KEY(id) REFERENCES images(id)
);

CREATE TABLE galleries (
    id SERIAL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    added_date DATE NOT NULL,

    PRIMARY KEY(id)
);

CREATE TABLE galleries_images (
    gallery_id INT,
    image_id CHAR(64),

    PRIMARY KEY(gallery_id, image_id),
    CONSTRAINT fk_gallery FOREIGN KEY(gallery_id) REFERENCES galleries(id),
    CONSTRAINT fk_image FOREIGN KEY(image_id) REFERENCES images(id)
);

CREATE VIEW search_pool AS
        SELECT id AS image_id, description AS value FROM images
UNION   SELECT id AS image_id, name AS value FROM tags;
