# De Jupyter a producción: cómo se trabaja de verdad con datos en Python

**Guion completo — Sesión en 42 Madrid · ~85 minutos + preguntas**

Materiales: este documento, el repo `charla-42-datos` (subido a GitHub antes de empezar, con QR en la primera diapositiva) y una terminal con el entorno ya montado (`.venv` creado, `pip install -r requirements.txt && pip install -e .` y el pipeline (`generate_sample_data.py` + `build_dataset.py`) ejecutados de antemano, y el comando `git checkout <commit>` ensayado como plan B).

Convención: en cada bloque tienes **EN PANTALLA** (lo que haces) y **GUION** (lo que dices, escrito para ser hablado; hazlo tuyo, no lo recites).

Audiencia: estudiantes de 42 Madrid. Vienen de C++, tienen buen nivel de terminal, git, y pensamiento de bajo nivel. La charla conecta constantemente con eso.

---

## Minuto 0–3 · Apertura: la pregunta

**EN PANTALLA:** Diapositiva 1: *"¿Cuánto NO₂ nos regala el tráfico de Madrid?"* y el QR del repo.

**GUION:**

"Buenas. Antes de hablar de Python, de pandas o de nada, quiero haceros una pregunta de Madrid: ¿cuánto de lo que respiráis cuando venís aquí, a Campus, lo ha puesto un coche? No es retórica: Madrid tiene una red de estaciones que miden la calidad del aire cada hora desde hace décadas, y los datos son públicos. Hoy vamos a responder esa pregunta con datos de verdad.

Pero la charla no va de calidad del aire. Va de algo que no os va a enseñar ningún tutorial: la diferencia entre *hacer un análisis* y *hacer un análisis del que alguien se pueda fiar*. Vosotros ya sabéis programar —venís de C++, de Makefiles, de pelearnos con la memoria—, y esa base es más valiosa de lo que pensáis. Lo que os falta no es código: es el oficio que hay alrededor. Y eso es exactamente lo que vamos a ver."

---

## Minuto 3–10 · El crimen: un notebook real

**EN PANTALLA:** Abres `notebooks/01_eda_horrible.ipynb`. Lo recorres celda a celda SIN arreglarlo todavía. Deja que el público encuentre los problemas: pídeselo explícitamente.

**GUION:**

"Esto es un notebook real. Bueno, lo he escrito yo para hoy, pero os juro que he visto peores cobrando sueldo de senior. Se llama —miradlo bien— `analisis FINAL v3 DEFINITIVO (este si)`. Si os reís es porque os ha pasado o porque os va a pasar.

Dadme un minuto y decidme qué está mal aquí. [Pausa real. Deja que hablen. Suelen salir: la ruta absoluta de Windows, las variables df2/df3/df_final, el código comentado 'porque peta'.]

Vamos a ponerle nombre a cada crimen. Uno: la ruta `C:\Users\dani\Desktop`. Este notebook solo funciona en un ordenador del planeta Tierra, y es el de Dani. Dos: `df`, `df2`, `df3`, `df_final`. Cada celda depende de haber ejecutado las anteriores *en un orden concreto que no está escrito en ningún sitio*. Si ejecutáis la celda 4 antes que la 3, obtenéis otro resultado, sin error. Tres, y este es el grave: mirad este comentario: 'salen muy pocas filas?? bueno da igual sigo'. Eso es un bug de datos. El filtro busca la estación 'Plaza Elíptica' escrita exactamente así, pero en los datos aparece también como 'PLAZA ELIPTICA' y como 'Pza. Elíptica'. El código no peta. Simplemente *calcula mal* y te lo dice con una sonrisa.

Y esa es la primera gran idea de la charla, apuntadla: **en software normal, los errores explotan; en datos, los errores te dan un número equivocado con cara de número correcto.** Un segfault es un regalo comparado con esto. Toda la ingeniería que vamos a ver hoy existe para defendernos de esa categoría de error."

---

## Minuto 10–18 · El mapa: el ecosistema en capas (para gente de C++)

**EN PANTALLA:** Diapositiva 3: el mapa en capas, NumPy → pandas/Polars → matplotlib → scikit-learn, y el taller. Señala los guiños a C++ en la diapositiva.

**GUION:**

"Antes de arreglar el desastre, el mapa del territorio. El ecosistema de Python para datos parece infinito, pero en realidad son cuatro piezas apiladas, y os lo cuento desde abajo porque viniendo de C++ es donde os vais a sentir en casa.

Abajo del todo, **NumPy**: arrays N-dimensionales. Lo que tenéis que entender —y que a la gente de Python puro le cuesta ver— es que un array de NumPy no es una lista de Python: es un bloque contiguo de memoria con un dtype fijo. Pensad en un `T*` con `malloc` y una cabecera de metadatos: shape, strides, dtype. Las operaciones no son bucles de Python: son rutinas BLAS/LAPACK compiladas en C y Fortran, muchas con instrucciones SIMD. Python no ejecuta la cuenta: la *despacha*. En la siguiente diapositiva os enseño los números.

Encima, **pandas**: el DataFrame, una tabla con columnas tipadas. Cada columna es, por debajo, un array de NumPy con un índice y manejo de valores perdidos. Es la herramienta con la que vais a pasar el 70% del tiempo, porque el 70% del trabajo real es limpiar y transformar tablas. Existe **Polars**, escrito en Rust, sin GIL, con paralelismo real y una API estricta que os va a recordar más a Rust que a Python. Y **DuckDB**, SQL analítico embebido. En 2026, para datasets de más de un par de gigas, son a menudo la respuesta correcta. Hoy uso pandas porque es la lengua franca que os vais a encontrar en cualquier empresa.

Al lado, **matplotlib**: gráficos. API fea, control absoluto. Y arriba **scikit-learn** para modelos clásicos: random forests, regresiones, SVMs... que por debajo son C++ y Cython. Hoy solo lo saludamos.

Y luego está el taller: **Jupyter** para explorar, **uv** para entornos y dependencias —escrito en Rust, resuelve en milisegundos lo que pip tardaba minutos—, **pytest** para tests y **ruff** como linter. La tesis de hoy: las cuatro librerías de arriba las aprende cualquiera en un mes. Lo que separa a un júnior de alguien con quien da gusto trabajar es el taller."

---

## Minuto 18–28 · Por debajo del capó: de C++ a NumPy

**EN PANTALLA:** Diapositiva 4: la comparativa memory layout (Python list vs NumPy), el benchmark 350×, y los tres insights. Si da tiempo, abre una terminal y ejecuta el benchmark en vivo (tenlo preparado):

```python
import numpy as np, time
a = list(range(10_000_000))
t=time.time(); [x+1 for x in a]; print(f"list comp: {time.time()-t:.2f}s")
a = np.arange(10_000_000)
t=time.time(); a+1; print(f"numpy:     {time.time()-t:.4f}s")
```

**GUION:**

"Esta diapositiva es para vosotros. Sé que cuando os dicen 'Python para datos es rápido' vuestra reacción es pensar 'Python no es rápido, punto'. Y tenéis razón... si estáis pensando en Python puro. Pero mirad esto.

A la izquierda, una lista de Python: un array de punteros a PyObjects. Cada elemento es un objeto completo con refcount, type pointer, cabecera... Cada acceso es una indirección y un cache miss casi garantizado. Vosotros que habéis trabajado con memoria en C++ sabéis lo que eso cuesta.

A la derecha, un array de NumPy: un bloque contiguo de float64 con stride de 8 bytes. Es exactamente lo que haríais con un `std::vector<double>`: datos apretados en memoria, cache-friendly. La diferencia es que NumPy le ha puesto un wrapper de Python encima que os deja operar con sintaxis de alto nivel.

Y aquí está el resultado: sumar 1 a 10 millones de elementos. Con un bucle for de Python: casi 3 segundos. Con NumPy, `a + 1`: 8 milisegundos. 350 veces más rápido. [Si ejecutas en vivo: 'vedlo vosotros mismos, no me creáis'.] ¿Por qué? Porque `a + 1` no ejecuta Python: despacha a una rutina en C que recorre el bloque contiguo con instrucciones vectorizadas. Python solo dice *qué* hacer; el *cómo* lo hace C, Fortran o, en el caso de Polars, Rust.

Tres cosas que os quiero que recordéis. Uno: la estructura de un ndarray —puntero, shape, strides, dtype— os tiene que sonar a un struct con un `T*` y metadatos; lo es. Dos: el hot path de casi todas las librerías de datos está en C/C++/Fortran: BLAS, LAPACK, SIMD. Python es el pegamento, no el motor. Tres: Polars va un paso más allá y usa Rust sin GIL, con paralelismo real y zero-copy. Si alguien del mundo de 42 quiere contribuir a librerías open source de datos, ahí hay sitio para gente que sabe C++ y Rust.

Moraleja: **Python para datos no es lento: es C, Fortran y Rust con un volante muy cómodo.** Y ahora que sabéis por qué es rápido, vamos a ver cómo se usa bien."

---

## Minuto 28–35 · Anatomía de un proyecto: estructura, entorno y datos inmutables

**EN PANTALLA:** Diapositiva 5. Terminal: `tree` del repo. Luego `requirements.txt` y `.gitignore` en el editor. Comando estrella: con el `.venv` ya activado, `pytest -v` en vivo.

**GUION:**

"Vale, vamos a arreglar el crimen. Lo primero no es código: es dónde vive cada cosa. Esta es la estructura, y es casi un estándar de facto en la industria. [Recorres el árbol.]

`data/raw` tiene una regla sagrada: **los datos crudos son inmutables**. Nunca, jamás, abrís el CSV y arregláis una celda a mano. ¿Por qué? Porque una edición manual es un cambio sin historia: dentro de tres meses nadie sabrá que pasó, ni por qué, ni podrá repetirlo con el archivo nuevo que llegue. Todo arreglo se hace en código, y así queda escrito, versionado y repetible. `data/processed` es donde caen los datos limpios, y fijaos en el `.gitignore`: los datos procesados no se commitean. Se *regeneran*. Si están en git, mienten: nadie sabe con qué versión del código se hicieron.

`src/airemad` es el paquete: el código de verdad. `notebooks` para explorar, `tests` para dormir tranquilos, `scripts` para los puntos de entrada.

Dos palabras sobre el entorno, que es la base de todo lo demás. `python -m venv .venv` crea un entorno virtual: una carpeta con su propio intérprete y sus propios paquetes, aislada de lo que tengáis instalado en el sistema. Lo activáis (`source .venv/bin/activate`) y a partir de ahí `pip install -r requirements.txt` instala exactamente las versiones que el archivo declara. Es el equivalente en Python a compilar dentro de un entorno controlado en vez de contra las librerías que haya sueltas en vuestro sistema: nada de 'en mi máquina funciona'. Resultado: cualquiera clona esto, hace `pip install -r requirements.txt`, y tiene *exactamente* mi entorno.

Y hay un `Makefile` en el repo —que en esta casa creo que no necesita presentación—, con targets `install`, `data`, `test`, `fclean` y `re`. [Sonrisa. Que noten que conoces la norminette.] Por debajo usa `uv`, una herramienta moderna escrita en Rust que hace lo mismo que `venv` + `pip` pero más rápido y con un lockfile que fija el árbol de dependencias entero. Para esta charla `venv` es la base porque no depende de instalar nada adicional y se explica en una frase; `uv` es la alternativa que os recomiendo mirar en cuanto salgáis de aquí.

Y la última línea del `.gitignore` que quiero que veáis: `.env`, credenciales, claves. **Eso no entra en git ni aunque el repo sea privado.** Un token commiteado es un token comprometido; hay bots escaneando GitHub para encontrarlos en segundos. Esto os lo digo una vez y os lo digo seria/o."

---

## Minuto 35–50 · La demo central: del caos al paquete

Es el corazón de la charla. Ritmo: enseñar el problema en el notebook → enseñar la solución en `src/` → ejecutar. No escribas el código en directo desde cero (riesgo y tiempo); ten el código hecho y *recórrelo* explicando decisiones, y ejecuta en vivo. Si algo se rompe: `git checkout <commit>` y a seguir.

**EN PANTALLA (35–40):** `data/raw/calidad_aire_madrid.csv` abierto en crudo (`head` en la terminal). Señalas los horrores: separador `;`, decimales con coma, `-999`, fechas mezcladas, nombres de estación inconsistentes.

**GUION:**

"Miremos los datos como llegan, que es algo que deberíais hacer siempre antes de escribir una línea: `head` al archivo. Separador punto y coma, clásico de la administración española. Decimales con coma: '48,3'. Eso significa que pandas va a leer la columna NO2 como *texto*, y `'48,3' > '5,1'` es una comparación de strings que os va a dar disgustos. Valores `-999`: es la forma noventera de decir 'no hay dato'; si no los quitáis, vuestra media de NO₂ sale negativa y nadie se entera. Fechas en dos formatos mezclados. Y la misma estación escrita de cuatro maneras. Esto no es un dataset saboteado: los datos públicos reales vienen *así o peor*. Bienvenidos al 70% del trabajo."

**EN PANTALLA (40–47):** `src/airemad/clean.py` en el editor. Recorres `parse_fechas`, `parse_decimales`, `sentinel_a_nan`, `normalizar_estaciones`, y al final la función `limpiar` con su cadena de `.pipe()`. Después `load.py` (30 segundos: una función carga, otra guarda, rutas relativas a la raíz del proyecto). 

**GUION:**

"Aquí está la limpieza convertida en ingeniería, y quiero que veáis tres decisiones de diseño, porque las decisiones son lo transferible.

Primera: **cada función hace una cosa**, recibe un DataFrame y devuelve uno nuevo, sin tocar el de entrada. Son funciones puras, como en programación funcional. ¿El premio? Esta belleza de aquí abajo: la función `limpiar` es una cadena de `.pipe()`, que se lee como una receta: parsea fechas, parsea decimales, quita centinelas, normaliza estaciones, quita duplicados. El orden importa y *está escrito*, no depende de en qué orden ejecutaste celdas un martes.

Segunda decisión, mirad `normalizar_estaciones`: si aparece una estación que no conozco, **lanzo una excepción**. No la ignoro, no pongo NaN y a correr: peto, alto y claro. Esto es lo contrario del 'bueno da igual sigo' del notebook horrible. En datos hay que convertir los errores silenciosos en errores ruidosos a propósito, porque ruidoso se arregla y silencioso se publica.

Tercera: el notebook hacía `df2`, `df3`, filtrando los -999 *después* de convertir... y se le olvidó un caso. Aquí cada paso tiene nombre, docstring y —ahora lo veis— test."

**EN PANTALLA (47–50):** Terminal, con el `.venv` ya activado: `python scripts/generate_sample_data.py && python scripts/build_dataset.py` (se ve el log: 2212 filas crudas → 2190 limpias, 64 nulos detectados). Luego `pytest -v` con los 7 tests en verde. Abres `tests/test_clean.py` y enseñas el fixture diminuto y el test de la excepción.

**GUION:**

"Y ahora, magia aburrida, que es la mejor magia: `python scripts/build_dataset.py`. Una orden, y el pipeline entero corre: 2212 filas crudas, 2190 limpias, 64 nulos detectados y declarados. Cualquiera de vosotros puede clonar el repo y obtener exactamente este resultado. Eso se llama reproducibilidad y en ciencia de datos es la diferencia entre conocimiento y anécdota.

¿Y cómo sé que la limpieza hace lo que creo? `pytest`. Miradlos: siete tests, y fijaos en el truco del fixture: no testeo contra el dataset real, me fabrico un DataFrame de tres filas que contiene *todos los problemas conocidos*: una fecha en cada formato, un -999, dos variantes del mismo nombre. Tests que corren en milisegundos. Y mi favorito: `test_normalizar_estaciones_falla_con_desconocidas`, un test que comprueba que el código *peta cuando debe petar*. Cada vez que los datos me sorprendan con un caso nuevo, el caso entra al fixture y ya nunca vuelve a sorprenderme. Así se acumula conocimiento sobre tus datos: en forma de tests."

---

## Minuto 50–58 · El premio: el notebook limpio y la respuesta a la pregunta

**EN PANTALLA:** `notebooks/02_eda_limpio.ipynb`. Lo ejecutas entero de arriba abajo (Run All, con teatro: "contened la respiración"). Aparecen los dos gráficos. Te detienes en el de laborable vs fin de semana.

**GUION:**

"Y ahora el premio. Este es el notebook después de la mudanza. Contad las líneas de código: unas diez. `limpiar(load_raw())` y a pintar. Todo lo demás es *narrativa*: qué pregunta hago, qué veo, qué concluyo. Esta es mi regla para los notebooks: **el notebook es el paper, el paquete es el laboratorio.** El notebook se lee; el código se importa. Y lo ejecuto entero, de arriba abajo, delante de vosotros, porque puedo: Run All. [Corre.] Esto, con el notebook horrible, era ruleta rusa.

Primer gráfico: NO₂ mensual por estación. Dos cosas. La forma de U: invierno alto, verano bajo —calefacciones más un fenómeno meteorológico precioso que se llama inversión térmica, que en Madrid en enero funciona como una tapa de olla—. Y la jerarquía: Plaza Elíptica, tráfico puro, arriba del todo, flirteando con el límite legal europeo, la línea roja. Casa de Campo, un parque, abajo. Misma ciudad, mismo día, el doble o el triple de NO₂ según cuántos coches tengas al lado.

Pero el segundo gráfico es mi favorito, porque es un experimento natural. Cada fin de semana Madrid hace, sin querer, ciencia: quita una parte enorme del tráfico y deja todo lo demás igual —misma meteorología, mismas calefacciones—. Si el NO₂ cae el sábado, esa caída es atribuible al coche. Y mirad: cae en todas las estaciones, y cae *más* donde más tráfico hay. Ahí tenéis la respuesta a la pregunta del principio, sin un solo modelo de machine learning: una resta bien hecha sobre datos bien limpiados. Que sea esta vuestra segunda gran idea del día: **la mayoría del valor en datos no viene del modelo, viene de la pregunta bien planteada y de los datos en los que puedes confiar.**"

---

## Minuto 58–63 · ¿Y después de esto qué? Tres caminos

**EN PANTALLA:** Diapositiva 8: los tres caminos.

**GUION:**

"Lo que habéis visto hoy es la base común. Desde aquí salen tres caminos, y los tres están bien pagados. Si os tira la *ingeniería*: pipelines, orquestación, calidad de datos a escala: data engineering, y vuestro perfil de 42 encaja como un guante, porque es ingeniería de software aplicada a datos. Si os tira el *modelado*: scikit-learn, después deep learning, MLOps para ponerlo en producción. Si os tira el *negocio*: análisis, visualización, contar historias con datos a gente que decide.

Mi consejo concreto, uno solo: elegid una pregunta vuestra —de verdad, que os pique— sobre datos abiertos de Madrid: BiciMAD, tráfico, terrazas, padrón... y hacedle a esa pregunta *todo* lo que hemos hecho hoy: repo, estructura, limpieza testeada, notebook narrativo, README. Ese proyecto, en una entrevista, vale más que tres certificados de Coursera, porque demuestra oficio, no asistencia."

---

## Minuto 63–70 · ¿Y qué hace un data scientist todo el día?

**EN PANTALLA:** Diapositiva 9: expectativa vs realidad, y las barras horizontales de reparto de tiempo.

**GUION:**

"Os acabo de enseñar tres caminos. Pero antes de que elijáis uno, quiero que veáis cómo es el día a día de verdad, porque si venís de programación pura es fácil tener una imagen equivocada del data scientist.

A la izquierda, lo que la gente cree: que pasamos el día entrenando redes neuronales, ajustando hiperparámetros y publicando en arXiv. A la derecha, lo que pasa de verdad: pasamos el día limpiando CSVs rotos, discutiendo con negocio qué demonios significa cada columna, y haciendo gráficos que conviertan un hallazgo en una decisión. Es menos glamuroso y mucho más artesano de lo que parece.

Mirad el reparto real de la semana. Un 45% se va en obtener, limpiar y entender los datos: hablar con la fuente, descubrir que los -999 existen, escribir la limpieza que acabamos de ver. Otro 25% es explorar, visualizar, iterar: los notebooks. Un 15% es comunicar resultados: reuniones, presentaciones, convencer a alguien de que tome una decisión basándose en lo que has encontrado. Y un 15% es el modelado propiamente dicho, el machine learning del que todo el mundo habla.

Es decir: el 70% del trabajo está *antes* del modelo. Y adivina qué: todo lo que hemos hecho hoy —la limpieza, la estructura, los tests, los gráficos que cuentan una historia— es exactamente ese 70%. No es 'lo aburrido antes de lo bueno': *es* el trabajo. El modelo es la guinda. Y si la base de datos está mal, el modelo estará mal también.

Y hay una consecuencia directa para vosotros: las habilidades que más importan en la práctica, por orden, son pensamiento crítico y formular buenas preguntas; luego SQL y pandas (manejarse con tablas); luego visualización y comunicación; y al final, por detrás, los algoritmos de ML. Curiosamente, la formación estándar va exactamente en orden inverso. Así que si hoy os ha parecido que hemos hablado poco de modelos... es porque esta charla refleja cómo se trabaja de verdad."

---

## Minuto 70–78 · Git para gente de datos + la frontera júnior/sénior

**EN PANTALLA:** Terminal: `git log --oneline` del repo (la historia cuenta la evolución). Luego `git diff` de un notebook con un cambio trivial de metadata. Después diapositiva 10: júnior vs sénior.

**GUION:**

"Dos minutos de git, porque vosotros ya sabéis git, pero los datos tienen dos trampas propias.

Primera, mirad el `git log` de este repo: la historia *es* la charla. Cada commit es un paso de la evolución que acabamos de hacer, y los mensajes explican el porqué. Commits atómicos con mensajes que cuentan una historia: eso vale el doble en datos, porque dentro de seis meses la pregunta nunca es '¿qué cambié?', es '¿por qué me creí este número en marzo?'.

Segunda trampa: los notebooks son JSON con las salidas embebidas dentro. Mirad este diff: he reejecutado una celda sin cambiar el código y git cree que ha cambiado medio archivo: contadores de ejecución, imágenes en base64... Los diffs de notebooks son ilegibles y los merges, imposibles. Soluciones, de menos a más: `nbstripout` para quitar las salidas antes de commitear, o `jupytext` para emparejar el notebook con un `.py` plano que es lo que versionas de verdad. Elegid una, pero elegid alguna.

Y ya que estamos, la frontera júnior/sénior. El júnior pregunta '¿qué modelo uso?'; el sénior pregunta '¿de dónde salen estos datos y qué les ha pasado por el camino?'. El júnior tiene un notebook que le funciona; el sénior tiene un repo que le funciona *a otra persona*. El júnior arregla el dato a mano y sigue; el sénior escribe la función, el test, y no vuelve a pensar en ello. Ninguna de las tres cosas requiere más talento. Requieren hábitos, y los hábitos se eligen."

---

## Minuto 78–83 · Cierre

**EN PANTALLA:** Diapositiva 11: las tres frases y el QR.

**GUION:**

"Resumen en tres frases, y os dejo en paz. Una: en datos, los errores no explotan, susurran; toda la ingeniería de hoy existe para hacerlos gritar. Dos: el notebook es el paper, el paquete es el laboratorio. Y tres: reproducible o no pasó.

El repo está en el QR: clonadlo, `python -m venv .venv`, `pip install -r requirements.txt`, `pytest -v`, y rompedlo, que para eso está. Las preguntas, ahora mismo y todas las que queráis."

---

## Apéndice A · Checklist de preparación

La semana antes: subir el repo a GitHub público y probar el quickstart completo en una máquina limpia (o un contenedor) siguiendo solo el README; preparar las 11 diapositivas (ya hechas, solo hay que pegar los QR en la 1 y la 11); generar el QR; ensayar la demo completa con cronómetro al menos dos veces; tener preparado el mini-benchmark de NumPy en un script (`benchmark.py`) para la slide 4.

El día antes: limpiar artefactos (`rm -f data/processed/*.parquet figures/*.png && rm -rf .pytest_cache`), borrar y recrear `.venv` desde cero (`rm -rf .venv`, luego `python -m venv .venv`, activar, `pip install -r requirements.txt && pip install -e .`) y volver a correr `python scripts/generate_sample_data.py && python scripts/build_dataset.py && pytest -v` para verificar que todo corre desde cero; dejar abiertos y ordenados terminal (fuente grande, tema claro si el proyector es malo, con el `.venv` ya activado), editor con los archivos clave en pestañas (`clean.py`, `test_clean.py`, `.gitignore`, `requirements.txt`) y JupyterLab con los dos notebooks; modo no molestar en el portátil.

Plan B por capas: si falla el directo, cada estado intermedio de la demo es un commit (`git log --oneline` y `git checkout` al punto que toque); si falla el entorno entero, capturas de pantalla de cada salida clave en las diapositivas de respaldo (la slide 4 tiene el benchmark impreso, la 7 tiene los gráficos); si falla el proyector, la charla se puede dar con el README impreso y carisma.

## Apéndice B · Preguntas que te van a hacer (y respuestas cortas)

"¿Pandas o Polars?" — Aprende pandas porque es lo que te vas a encontrar; juega con Polars porque es probablemente el futuro y te hará mejor incluso en pandas (su API te obliga a pensar en expresiones, no en bucles). Polars está escrito en Rust con binding Python, sin GIL, con ejecución lazy y paralelismo real: si os mola la ingeniería de bajo nivel, el repo de Polars es una lectura increíble.

"¿Por qué Python y no C++ para datos?" — Porque el trabajo es iterar rápido: cambiar una pregunta, re-limpiar, probar otra transformación, comunicar. Ese ciclo necesita un lenguaje que priorice la productividad del humano. Pero el motor que ejecuta la cuenta *es* C/C++/Rust, así que no estáis abandonando el rendimiento: estáis delegando el cuándo usarlo. La analogía: no escribís un Makefile en ensamblador.

"¿Por qué no usas IA para limpiar los datos?" — La uso para *escribir* el código de limpieza más rápido; lo que no delego es la decisión de qué es un dato válido ni el test que lo verifica. La IA acelera el oficio, no lo sustituye: si no sabes lo que hemos visto hoy, no puedes ni revisar lo que te genera.

"¿Cuándo uso un modelo de ML?" — Cuando una pregunta bien planteada sobre datos limpios no se pueda responder con una agregación. Es decir: más tarde de lo que crees.

"¿Notebooks en producción?" — Como regla, no: en producción van scripts/paquetes testeados; el notebook es exploración y comunicación. (Existen excepciones tipo Papermill, pero que sean excepciones.)

"¿Esto del -999 es real?" — Dolorosamente real. Centinelas tipo -999, 9999 o 0 significando 'sin dato' aparecen en datos meteorológicos, sensores y administraciones de medio mundo. Por eso el primer paso siempre es mirar el archivo crudo y la documentación de la fuente.

"¿Y conda?" — Sigue existiendo y domina en entornos científicos pesados (CUDA, geoespacial), pero para proyectos estándar en 2026, uv + pyproject.toml es más simple, más rápido y más estándar.

"¿Puedo contribuir a librerías de datos sin saber ML?" — Absolutamente. NumPy, Polars, DuckDB, Arrow y uv son proyectos de ingeniería de sistemas pura. Si sabéis C++ o Rust y os interesa el open source, ahí sobra trabajo y faltan manos. Muchos committers entraron sin saber una línea de ML.

"¿Cuánto gana un data scientist?" — Depende mucho, pero en España (Madrid/Barcelona) en 2026 un perfil junior entra en torno a 28-35k y un sénior ronda los 50-70k. En remoto para empresas USA o UK los rangos suben sensiblemente. Data engineering y MLOps tienden a la parte alta del rango.
