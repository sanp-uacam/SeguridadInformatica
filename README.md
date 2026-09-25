<h1 align="center">🔒 Seguridad Informática</h1>

<p align="center">
  <strong>Prácticas de la asignatura</strong><br>
  Facultad de Ingeniería · Universidad Autónoma de Campeche (UACAM)
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+"/>
  <img src="https://img.shields.io/badge/Prácticas-3-6950A1?style=for-the-badge" alt="3 prácticas"/>
  <img src="https://img.shields.io/badge/Estado-Completas-success?style=for-the-badge" alt="Completas"/>
</p>

---

## 📚 Prácticas

| # | Práctica | Tema | Tecnología | Documentación |
|---|----------|------|------------|---------------|
| 2 | [**P02-RSA**](P02-RSA) | Algoritmo RSA: generación de claves y descifrado de un criptograma | Python puro (sin librerías) | [README](P02-RSA/README.md) |
| 3 | [**P03-HIBRIDO**](P03-HIBRIDO) | Cifrado híbrido: AES-256-CBC para el mensaje + RSA-2048-OAEP para la clave | `pycryptodome` | [README](P03-HIBRIDO/README.md) |
| 4 | [**P04-HASH**](P04-HASH) | Control de acceso con funciones hash SHA-256 y validación de contraseñas | Tkinter (librería estándar) | [README](P04-HASH/README.md) |

Cada carpeta tiene su propio README con la explicación completa, las instrucciones para ejecutarla
y las **capturas de los resultados** en la subcarpeta `capturas/`.

---

## ⚡ Ejecución rápida

```bash
git clone https://github.com/KevinUac/SeguridadInformatica.git
cd SeguridadInformatica
```

| Práctica | Comando |
|----------|---------|
| **P02 — RSA** | `cd P02-RSA && python rsa_practica2.py` |
| **P03 — Híbrido** | `cd P03-HIBRIDO && pip install -r requirements.txt && python hibrido_rsa_aes.py` |
| **P04 — Hash** | `cd P04-HASH && python main.py` |

Solo la Práctica 3 necesita instalar algo (`pycryptodome`); las otras dos funcionan con la
librería estándar de Python.

---

## 🧭 Recorrido de las prácticas

Las tres prácticas van armando el panorama completo de la criptografía aplicada:

```
P02  →  Criptografía asimétrica "a mano"
        Entiendo cómo nacen las claves RSA y por qué funciona el descifrado.
              │
              ▼
P03  →  Criptografía híbrida (lo que se usa en la vida real)
        Junto la velocidad del cifrado simétrico con el intercambio seguro del asimétrico.
              │
              ▼
P04  →  Funciones hash
        Ya no se trata de recuperar el dato, sino de verificarlo sin guardarlo.
```

---

## 🧑‍🎓 Datos académicos

| Campo | Detalle |
|-------|---------|
| 📚 **Materia** | Seguridad Informática |
| 🏫 **Institución** | Facultad de Ingeniería — UACAM |
| 👨‍💻 **Alumno** | Kevin del Jesús González Maas |
| 👨‍🏫 **Docente** | Sergio A. Noh Puch |
| 🎓 **Grado / Grupo** | 7° semestre, Grupo "A" |

---

<p align="center">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" width="40"/>
  &nbsp;&nbsp;
  <strong>Hecho con Python</strong> 🐍
</p>
