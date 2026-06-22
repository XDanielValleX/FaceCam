def buscar_persona_id(
        cursor,
        nombre
):

    cursor.execute(
        """
        SELECT id
        FROM personas
        WHERE nombre = %s
        """,
        (nombre,)
    )

    resultado = cursor.fetchone()

    if resultado is None:

        return None

    return resultado[0]