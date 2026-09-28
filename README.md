# Analizador Léxico Gráfico con FLEX

Aplicación de escritorio para Linux que analiza un subconjunto de C. La interfaz está escrita en **Python con GTK 4 + Libadwaita (PyGObject)** y usa un motor en **C generado por FLEX** para el análisis léxico. No utiliza una interfaz de consola.

## Requisitos y uso

En Fedora:

```bash
sudo dnf install flex gcc make python3-gobject gtk4 libadwaita
make
make run
```

En Debian/Ubuntu, instalar `flex`, `build-essential`, `make`, `python3-gi`, `gir1.2-gtk-4.0` y `gir1.2-adw-1`.

`make dist` prepara `dist/analizador_lexico` (interfaz ejecutable Python) y `dist/analizador_lexico_engine` (motor FLEX). Ambos archivos deben permanecer juntos; el equipo destino requiere Python 3, PyGObject y GTK 4.

El ejecutable incluido es para **Linux**. Windows no puede abrir binarios Linux; para entregar en Windows debe prepararse un paquete `.exe` allí, con Python, GTK 4, Libadwaita y el motor FLEX incluidos. El código fuente sí funciona en ambos sistemas cuando se instalan esas dependencias.

## Lenguaje reconocido

El programa analiza léxicamente C simplificado; no compila ni ejecuta el código.

| Categoría | Elementos reconocidos |
| --- | --- |
| Palabras reservadas | `int`, `if`, `else` |
| Identificadores | Empiezan con letra o `_`; después admiten letras, dígitos y `_` |
| Literales | Enteros positivos |
| Operadores | `+ - * / =` |
| Delimitadores | `; ( ) { }` |

Cada token muestra su lexema y categoría. La tabla se actualiza automáticamente después de una pausa breve al escribir. La aplicación informa cualquier símbolo que no pertenezca al lenguaje reducido.

## Cómo funciona FLEX y el autómata

FLEX transforma las expresiones regulares de `src/lexer.l` en un **autómata finito determinista (AFD)**. El AFD lee de izquierda a derecha y elige la coincidencia válida más larga. Al aceptar una cadena, la acción de la regla crea un token; para espacios y comentarios no se crea ninguno.

El diagrama para exponer está en [AUTOMATA.md](AUTOMATA.md). Al leer una letra o `_`, el AFD entra al estado de identificador; si el lexema completo es `int`, `if` o `else`, se clasifica como palabra reservada. Si lee un dígito, reconoce un entero.

## Estructura y pruebas

- `src/lexer.l`: reglas FLEX y acciones del AFD.
- `app.py`: aplicación gráfica GTK 4 escrita en Python.
- `src/lex.yy.c`: fuente C generado por FLEX durante la compilación.
- `examples/valido.c` y `examples/errores.c`: pruebas manuales.
- `PRESENTACION.md`: guion para presentar en clase.

Pruebe primero `examples/valido.c`: debe listar tokens sin errores. Luego abra `examples/errores.c`: debe señalar `@` como símbolo inválido.
