// OTL (Open Trading Language) v0.1 — ANTLR4 grammar (spec / optional codegen).
// MarketLab ships a hand-written parser in python/Gaffer/otl/parse.py aligned with this EBNF.
//
// shader Example(float alpha = 0.0, string tag = "x") {
//   signal(alphaWeight = alpha, confidence = 1.0, halfLife = 21.0, maxImpactFrac = 0.05, regimeCondition = tag, sideBet = false);
// }

grammar OTL;

shader
    : SHADER IDENT '(' paramList? ')' '{' body '}' EOF
    ;

paramList
    : param (',' param)*
    ;

param
    : TYPE IDENT ('=' expr)?
    ;

body
    : SIGNAL '(' signalArgs ')' ';'
    ;

signalArgs
    : signalArg (',' signalArg)*
    ;

signalArg
    : IDENT '=' expr
    ;

expr
    : expr op=('*'|'/'|'%') expr
    | expr op=('+'|'-') expr
    | '-' expr
    | '(' expr ')'
    | literal
    | IDENT
    | IDENT '(' argList? ')'
    ;

argList
    : expr (',' expr)*
    ;

literal
    : FLOAT_LIT
    | INT_LIT
    | STRING_LIT
    | BOOL_LIT
    ;

TYPE
    : 'float' | 'int' | 'string' | 'bool'
    ;

SIGNAL
    : 'signal'
    ;

SHADER
    : 'shader'
    ;

BOOL_LIT
    : 'true' | 'false'
    ;

STRING_LIT
    : '"' ( ~["\\] | '\\' . )* '"'
    ;

FLOAT_LIT
    : [0-9]+ '.' [0-9]* ([eE] [+-]? [0-9]+)?
    | [0-9]+ [eE] [+-]? [0-9]+
    ;

INT_LIT
    : [0-9]+
    ;

IDENT
    : [a-zA-Z_][a-zA-Z0-9_]*
    ;

WS
    : [ \t\r\n]+ -> skip
    ;

LINE_COMMENT
    : '//' ~[\r\n]* -> skip
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;
