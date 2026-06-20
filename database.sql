CREATE TABLE personas(
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100)
);

CREATE TABLE camaras(
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100)
);

CREATE TABLE detecciones(
    id SERIAL PRIMARY KEY,
    persona_id INTEGER NOT NULL,
    camara_id INTEGER NOT NULL,
    fecha_hora TIMESTAMP NOT NULL,

    CONSTRAINT fk_persona
        FOREIGN KEY (persona_id)
        REFERENCES personas(id),

    CONSTRAINT fk_camara
        FOREIGN KEY (camara_id)
        REFERENCES camaras(id)
);