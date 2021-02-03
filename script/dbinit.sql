-- https://stackoverflow.com/a/10267699/13401153
CREATE TABLE images (
    id VARCHAR(32),
    description VARCHAR(255),
    added_date DATE,
    content BYTEA,

    PRIMARY KEY(id)
);

CREATE TABLE thumbnails (
    id VARCHAR(32),
    content BYTEA,

    PRIMARY KEY(id),
    CONSTRAINT fk_image FOREIGN KEY(id) REFERENCES images(id)
);

CREATE TABLE metadata (
    id VARCHAR(32),

    -- TODO: which fields are metadata?

    PRIMARY KEY(id),
    CONSTRAINT fk_image FOREIGN KEY(id) REFERENCES images(id)
);

CREATE TABLE galleries (
    id SERIAL,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    added_date DATE,

    PRIMARY KEY(id)
);

CREATE TABLE galleries_images (
    gallery_id INT,
    image_id VARCHAR(32),

    PRIMARY KEY(gallery_id, image_id),
    CONSTRAINT fk_gallery FOREIGN KEY(gallery_id) REFERENCES galleries(id),
    CONSTRAINT fk_image FOREIGN KEY(image_id) REFERENCES images(id)
);
