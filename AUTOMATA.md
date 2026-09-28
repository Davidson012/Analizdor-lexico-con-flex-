# Autómata léxico simplificado

```mermaid
stateDiagram-v2
    [*] --> Inicio
    Inicio --> Identificador: letra o _
    Identificador --> Identificador: letra, dígito o _
    Identificador --> Token: separador
    Token --> Reservada: coincide con palabra reservada
    Token --> Id: en otro caso
    Inicio --> Entero: dígito
    Entero --> Entero: dígito
    Entero --> Token: separador
    Inicio --> Operador: + - * / =
    Inicio --> Delimitador: ; ( ) { }
    Inicio --> Error: otro símbolo
```

Los estados `Token`, `Id`, `Reservada`, `Entero`, `Operador` y `Delimitador` representan aceptación. FLEX implementa estos recorridos automáticamente desde las expresiones regulares; el diagrama es una representación conceptual del AFD generado.
