# Práctica 2doParcial: Login SQL Injection y Remedación mediante Parametrización

**Materia:** Seguridad Informática  
**Docente:** Ing. Sergio Noh Puch  
**Estudiante:** Fernando Adriano Sabido Quijano (Matrícula: 66744)  
**Grupo:** 7.º "A" - Facultad de Ingeniería, UACAM  
**Rama Git:** `66744_SABIDO`  

---

## Estructura del Repositorio

- `login/login_vulnerable.php`: Código PHP vulnerable a autenticación bypass mediante inyección SQL.
- `login/login_seguro.php`: Versión mitigada utilizando consultas parametrizadas PDO (Prepared Statements).
- `login/schema.sql`: Estructura de la base de datos de prueba (`seguridad_db`).
- `login/README.md`: Documentación y reporte del proceso de inyección y remedición.

## Payloads de Inyección SQL Probados

1. `admin' -- ` -> Omite la validación de contraseña comentando el resto de la consulta.
2. `' OR '1'='1' -- ` -> Fuerza la condición a VERDADERO, retornando el primer registro (`admin`).
3. `' OR 1=1 #` -> Bypass utilizando sintaxis de comentario MySQL `#`.
4. `admin' #` -> Autenticación directa como `admin`.

## Instrucciones para subir al repositorio de la clase (`sanp-uacam/SeguridadInformatica`)

1. Descomprimir este archivo ZIP.
2. Copiar la carpeta `login` directamente en la raíz de tu repositorio local `SeguridadInformatica`.
3. Asegurarte de estar en la rama `66744_SABIDO`:
   ```bash
   git checkout 66744_SABIDO
   ```
4. Agregar los cambios y realizar el commit:
   ```bash
   git add login/
   git commit -m "solucione el error de vulnerabilidad con las inyecciones sql"
   git push origin 66744_SABIDO
   ```
5. En GitHub, abrir el **Pull Request** desde `66744_SABIDO` hacia `main` del repositorio del profesor `sanp-uacam/SeguridadInformatica`.
