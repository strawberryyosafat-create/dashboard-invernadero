import duckdb

def cargar_datos():
    con = duckdb.connect(":memory:")
    con.execute("SELECT setseed(0.42)")

    # Paso 1: variables aleatorias base
    con.execute("""
        CREATE TABLE base AS
        SELECT
            i AS parcela_id,
            ROUND(100 + random() * 200, 2) AS volumen_riego,    -- 100 a 300 m3/ha
            ROUND(50  + random() * 100, 2) AS fertilizante_kg,  -- 50 a 150 kg/ha
            random()                       AS p,                -- para asignar tratamiento
            random() * 1.6 - 0.8           AS ruido             -- -0.8 a +0.8
        FROM generate_series(1, 100) t(i)
    """)

    # Paso 2: tabla final con la ecuación del rendimiento
    con.execute("""
        CREATE TABLE telemetria AS
        SELECT
            parcela_id, volumen_riego, fertilizante_kg,
            CASE WHEN p < 0.5 THEN 'Tratamiento_A' ELSE 'Tratamiento_B' END AS tipo_tratamiento,
            ROUND(5.0 + 0.035*volumen_riego + 0.020*fertilizante_kg
                  + CASE WHEN p >= 0.5 THEN 1.8 ELSE 0 END + ruido, 2) AS rendimiento_ton
        FROM base
    """)

    # Paso 3: extraer a pandas
    df = con.execute("SELECT * FROM telemetria ORDER BY parcela_id").df()
    return df

if __name__ == "__main__":
    df = cargar_datos()
    print(df.head(10))
    print(df.rendimiento_ton.describe())