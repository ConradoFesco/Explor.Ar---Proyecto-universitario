Las guías de estilo ayudan a los equipos de desarrollo a escribir código consistente simplificando su entendimiento a todos/as los/as miembros del equipo.
Python define en PEP8 como guía de estilos base y en PEP257 la convención para Docstrings. Teniendo esta referencia vamos a mencionar las normas mas importantes que esperamos que traten de cumplir en el trabajo.


Generales:
Uso de 4 espacios en lugar de tabs. Esto puede ser configurado en su editor
120 es el máximo de caracteres por línea. Preferentemente 80
Dejar 2 líneas en blanco entre clases y funciones
1 línea en blanco dentro de la clases entre los métodos de la misma
No dejar líneas en blanco luego de la línea def
No dejar espacios dentro de los paréntesis, corchetes y las llaves
Rodear los operadores con un espacio en blanco de ambos lados
No usar espacios en blanco alrededor del = cuando se pasa un keyword argument o se define un valor por defecto en una función
Usar líneas en blanco para la separación de lógica dentro de las funciones/métodos siempre que esté justificado
Mover los argumentos de una función de una nueva línea con indentación si no entran todos en la primer línea
Mover las condiciones a nuevas líneas si no entran en el máximo determinado. Esto te ayudará a entender la condición mirando de arriba hacia abajo.
Usar Strings multilíneas sin \\.
Use argumentos nombrados para aumentar la legibilidad.
Nunca termines tus líneas con punto y coma y no las uses para tener dos sentencias en la misma línea.
El encadenamiento de métodos debe ser separado en múltiples líneas para mejor legibilidad
Siempre comience el bloque de código en una nueva línea
Separa el símbolo # del contenido del comentario con un espacio en blanco

Nombres:
Usar snake_case para módulos, variables, atributos, funciones y nombre de métodos. NO USAR CamelCase.
Usar CamelCase para el nombre de las clases.
Los nombres deben referirse a lo que hace o contiene la variable, clase o función.
No incluya el tipo de la variable en su nombre. Ej: use personas en lugar de lista_personas.

Docstrings:
Escriba los docstrings contenidos con triple comillas dobles """

Escriba los docstrings para métodos que no sean tan simples. En los mismos resuma descripción de comportamiento, argumentos, valores de retorno, excepciones que se pueden lanzar

Imports:
Evite los import relativos utilice import absolutos
Nunca use * en los imports. Siempre sea explícito sobre lo que va a importar
Los imports deben escribirse en el siguiente orden separados por una línea:
Módulos build-in (que vienen con Python)
Módulos third-party (paquetes externos que instaló)
Módulos del proyecto actual

Malas ideas:
Variables globales
Usar lambdas donde no se requiere
Usar funciones embebidas

Fuentes:
PEPs
PEP8
PEP257