-- https://stackoverflow.com/a/10267699/13401153
CREATE TABLE images (
    id CHAR(64),
    description VARCHAR(255),
    added_date DATE NOT NULL,
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

    -- TODO: which fields are metadata?

    PRIMARY KEY(id),
    CONSTRAINT fk_image FOREIGN KEY(id) REFERENCES images(id)
);

CREATE TABLE galleries (
    id SERIAL,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255),
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
