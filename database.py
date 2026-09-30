import sqlite3

conn = sqlite3.connect("proformas.db")

cursor = conn.cursor()

# TABLA PROFORMAS

cursor.execute("""
CREATE TABLE IF NOT EXISTS proformas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proveedor TEXT,
    descripcion TEXT,
    cantidad REAL,
    precio REAL,
    subtotal REAL,
    iva REAL,
    total REAL,
    moneda TEXT,
    impuesto TEXT,
    fecha_creacion TEXT,
    ruta_pdf TEXT
)
""")

# TABLA PROVEEDORES

cursor.execute("""
CREATE TABLE IF NOT EXISTS proveedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    cedula TEXT,
    telefono TEXT,
    correo TEXT
)
""")

conn.commit()
conn.close()

print("Base creada correctamente")
