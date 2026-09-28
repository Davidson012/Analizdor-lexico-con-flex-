# Exposición breve: Analizador Léxico con FLEX

1. Un analizador léxico lee caracteres y los convierte en **tokens**.
2. El lenguaje reconoce `int`, `if`, `else`, identificadores, enteros, operadores y delimitadores.
3. FLEX convierte las expresiones regulares de `lexer.l` en un autómata finito determinista.
4. Abrir `examples/valido.c` y pulsar **Analizar**.
5. Explicar: `int` es reservada; `x` es identificador; `10` es entero; `=` es operador y `;` es delimitador.
6. Abrir `examples/errores.c`: `@` no pertenece al lenguaje y se reporta como símbolo inválido.
