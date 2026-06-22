def guardar_deteccion(
        cursor,
        conn,
        persona_id,
        camara_id,
        fecha_hora
):

    cursor.execute(
        """
        INSERT INTO detecciones
        (
            persona_id,
            camara_id,
            fecha_hora
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
        """,
        (
            persona_id,
            camara_id,
            fecha_hora
        )
    )

    conn.commit()