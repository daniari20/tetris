# Definición del agente basado en utilidad para el juego de tetris

-----

**Integrantes**
 - Daniela Ariadna Rueda Hernández
 - Silvana Suarez Caravajal
 - Camilo Andrés Medina Sánchez

Universidad Nacional de Colombia 
Introducción a los sistemas inteligentes
Primer semestre de 2026

----

## Representación del tablero - Estado 

El tablero del Tetris en el modo del torneo - Blitz se ve de la siguiente manera: 
![Tablero tetris](./media/tablero.png)
Matemáticamente el tablero se puede tratar como una matriz de la forma.

$$M = \begin{pmatrix} tab_{1,0} &  ... & tab_{1,10} \\ \vdots & \ddots & \vdots \\  tab_{20,0} & ... & tab_{20,10}\end{pmatrix}$$

Además, la representación del estado de las celdas, se desarrolla en un formato binario, siendo este: 
- 1: Celda ocupada
- 0: Celda vacía

----

## Acciones

Las acciones posibles son todas las formas de colocar las piezas