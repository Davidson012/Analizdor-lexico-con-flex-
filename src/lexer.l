%option noyywrap nodefault nounput noinput main

%{
#include <stdio.h>

/* Imprime: registro, categoría y lexema. */
#define TOKEN(tipo) printf("T\t%s\t%s\n", tipo, yytext)
#define ERROR(tipo) printf("E\t%s\t%s\n", tipo, yytext)
%}

IDENT   [a-zA-Z_][a-zA-Z0-9_]*
ENTERO  [0-9]+

%%

[ \t\r\n]+                     ;
"int"|"if"|"else"              { TOKEN("RESERVADA"); }
{IDENT}                           { TOKEN("IDENTIFICADOR"); }
{ENTERO}                          { TOKEN("ENTERO"); }
"+"|"-"|"*"|"/"|"="            { TOKEN("OPERADOR"); }
";"|"("|")"|"{"|"}"           { TOKEN("DELIMITADOR"); }
.                                { ERROR("SIMBOLO_INVALIDO"); }

%%
