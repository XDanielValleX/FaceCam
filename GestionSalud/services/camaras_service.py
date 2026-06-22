def buscar_camara_id(
        cursor,
        nombre
):

    cursor.execute(
        """
        SELECT id
        FROM camaras
        WHERE nombre = %s
        """,
        (nombre,)
    )

    resultado = cursor.fetchone()

    if resultado is None:

        return None

    return resultado[0]