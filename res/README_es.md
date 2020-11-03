<img align="left" width="80" height="80" src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/icon.jpg" alt="Insomniac">

# Insomniac
![PyPI](https://img.shields.io/pypi/v/insomniac?label=latest%20version)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/insomniac)
![PyPI - Downloads](https://img.shields.io/pypi/dm/insomniac)


[inglés](https://github.com/alexal1/Insomniac/blob/master/README.md) | [portugués](https://github.com/alexal1/Insomniac/blob/master/res/README_pt_BR.md)

Dale like y sigue automáticamente en tu teléfono / tableta Android. No se requiere root: funciona con [UI Automator](https://developer.android.com/training/testing/ui-automator?hl=es), que es una estructura de prueba oficial UI de Android.

<img src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/demo.gif">

### Índice
- [¿Por qué debería automatizar la actividad de Instagram (me gusta, seguir, etc.)?](#por-qu%C3%A9-deber%C3%ADa-automatizar-la-actividad-de-instagram-me-gusta-seguir-etc)
- [Cómo instalar](#c%C3%B3mo-instalar)
    * [Cómo instalar en Raspberry Pi OS](#c%C3%B3mo-instalar-en-raspberry-pi-os)
- [Comenzando](#comenzando)
    * [Ejemplo de uso](#ejemplo-de-uso)
    * [Lista completa de argumentos de la línea de comandos](#lista-completa-de-argumentos-de-la-l%C3%ADnea-de-comandos)
    * [FAQ](#faq)
- [Recursos extras](#recursos-extras)
- [Código fuente](#c%C3%B3digo-fuente)
- [Filtrando](#filtrando)
- [Whitelist y Blacklist](#whitelist-y-blacklist)
- [Análisis](#an%C3%A1lisis)
- [Recursos en progreso](#recursos-en-progreso)
- [¿Por qué Insomniac?](#por-qu%C3%A9-insomniac)
- [Comunidad](#comunidad)

### ¿Por qué debería automatizar la actividad de Instagram (me gusta, seguir, etc.)?
💸 Si solo desea aumentar el número de seguidores u obtener más me gusta, hay un montón de compañías que le darán eso de inmediato por unos pocos $$$. Pero lo más probable es que su audiencia sean bots y seguidores de masa.

🌱 Si desea obtener seguidores comprometidos, que estarán interesados en su contenido y probablemente le pagarán por sus servicios, entonces la _automatización_ es la manera correcta.

🎯 Este bot de Instagram le proporciona métodos para **alcanzar** a la audiencia que probablemente esté **interesada en usted**. Estos métodos son:
1. Interactuar con seguidores de **blogueros** con contenido similar
2. Interactuar con los que le gusten los **hashtags** que use
3. **Filtra** cuentas para evitar bots y seguidores de masa

📈 Usar estos métodos en conjunto da el mejor resultado.

### Cómo instalar
1. Instale el paquete **insomniac**: Ejecute `python3 -m pip install insomniac` en la terminal (Símbolo del sistema)<br/><sub><sup>Siempre que **python** y **pip** ya estén instalados. Aprenda <a href="https://github.com/alexal1/Insomniac/wiki/Install-Python">a comprobarlo</a>.</sup></sub>
2. Guarda el archivo [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) a un directorio desde el que va a iniciar el script (haga clic con el botón derecho en el enlace, luego Guardar como / Descargar link como)
3. Download y unzip [Android platform tools](https://developer.android.com/studio/releases/platform-tools), moverlos a un directorio donde no los eliminará accidentalmente. 
El lugar estándar es `C:\android-sdk\` (Windows), `~/Library/Android/sdk` (Linux/macOS)
4. [Agregue la ruta de platform-tools a las variables de entorno del sistema](https://github.com/alexal1/Insomniac/wiki/Agregue-la-ruta-de-platform-tools-a-las-variables-de-entorno-del-sistema-es). Si lo hace correctamente, el comando en la terminal (Símbolo del sistema) `adb devices` imprimirá `List of devices attached`

### Cómo instalar en Raspberry Pi OS
1. Update apt-get: `sudo apt-get update`
2. Instalar ADB y Fastboot: `sudo apt-get install -y android-tools-adb android-tools-fastboot`
3. Instale el paquete **insomniac**: Ejecute `python3 -m pip install insomniac` en la terminal
4. Guarda el archivo [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) a un directorio desde el que va a iniciar el script (haga clic con el botón derecho en el link, luego Guardar como / Descargar link como)

_IMPORTANTE: si utilizó anteriormente la versión 2.x.x, el archivo insomniac.py entrará en conflicto con el paquete insomniac. Entonces, guarde el start.py en una carpeta distinta_

### Comenzando
1. Conecte el dispositivo Android a su computadora con un cable USB
2. Habilite [Opciones para desarrolladores](https://developer.android.com/studio/debug/dev-options?hl=es) en el dispositivo
>En Android 4.1 y versiones anteriores, la pantalla Opciones para desarrolladores está disponible de forma predeterminada. En Android 4.2 y versiones posteriores, debes habilitarla. Si quieres habilitar las Opciones para desarrolladores, presiona la opción Número de compilación 7 veces. Puedes encontrar esta opción en una de las siguientes ubicaciones, según tu versión de Android:
>
> Android 9 (API nivel 28) y versiones posteriores: Configuración > Acerca del dispositivo > Número de compilación
>
> Android 8.0.0 (API nivel 26) y Android 8.1.0 (API nivel 26): Configuración > Sistema > Acerca del dispositivo > Número de compilación
>
> Android 7.1 (API nivel 25) y versiones anteriores: Configuración > Acerca del dispositivo > Número de compilación
3. Active **Depuración de USB** (e **Instalación de aplicaciones a través de USB** si existe tal opción) en la pantalla de opciones para desarrolladores.
4. El dispositivo le pedirá que permita la conexión de la computadora. Presione "Conectar"
5. Escriba `adb devices` en terminal. Mostrará los dispositivos conectados. Debe haber exactamente un dispositivo. Luego ejecute el script (funciona en Python 3):
6. Abra la terminal (Símbolo del sistema) en la carpeta con [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) descargado (o escribe `cd <camino-para-start.py>`) y ejecuta
```
python3 start.py --interact @netgeo
```
Asegúrese de que la pantalla esté encendida y que el dispositivo esté desbloqueado. No tiene que abrir la aplicación de Instagram, la secuencia de comandos la abre y se cierra cuando está terminada. Solo asegúrate de que la aplicación de Instagram esté instalada. Si todo está bien, el script abrirá los seguidores de `@natgeo` y les gustará sus publicaciones.

### Ejemplo de uso
Digamos que tienes un blog de viajes. Entonces es posible que desee utilizar dicha configuración:
```
python3 start.py --interact @natgeo amazingtrips beautifuldestinations --interactions-count 20-30 --likes-count 1-3 --follow-percentage 20 --repeat 120-180
```
El script interactuará secuencialmente con 20-30 seguidores de `@natgeo`, 20-30 usuarios que les gusta publicaciones de `#amazingtrips`, y 20-30 usuarios que les gusta publicaciones de `#beautifuldestinations`. Durante cada interacción, Insomniac dará 1-3 me gusta en publicaciones aleatorias y también seguirá al 20% de los usuarios interactuados. Una vez terminado, cerrará la aplicación de Instagram y esperará entre 120 y 180 minutos. Entonces el script repetirá lo mismo (y se repetirá infinitamente), pero los usuarios ya interactuados serán ignorados. La lista de fuentes (`@natgeo`, `#amazingtrips` y `#beutifuldestinations`) se barajará cada vez.

Toda esta aleatoriedad hace que sea muy difícil para Instagram detectar que estás usando un bot. Sin embargo, tenga cuidado con la cantidad de interacciones, porque incluso un humano puede tener un ban por violar los límites.

### Lista completa de argumentos de la línea de comandos
También puede ver esta lista ejecutando sin argumentos: `python3 start.py`.
```
  --interact username1 [username2 ...]
                        lista de usernames con cuyos seguidores desea
                        interactuar.
  --likes-count 2-4     número de likes para cada usuario interactuado, 2 por defecto.
                        Puede ser un número (Ej. 2) o un rango (Ej. 2-4).
  --total-likes-limit 300
                        límite en la cantidad total de likes durante la sesión, 300
                        por defecto.
  --interactions-count 60-80
                        cantidad de interacciones por cada blogger, 70 por
                        defecto. Puede ser un número (Ej. 70) o un rango
                        (Ej. 60-80). Solo cuentan las interacciones exitosas
  --repeat 120-180      repita la misma sesión nuevamente después de N minutos
                        completos, deshabilitada por defecto. Puede ser un numero
                        en minutos (Ej. 180) o un rango (Ej. 120-180).
  --follow-percentage 50
                        segue el porcentaje dado de usuarios, 0 por defecto.
  --follow-limit 50     límite en la cantidad de seguidores durante la interacción con
                        los seguidores de cada usuario, deshabilitada por defecto
  --unfollow 100-120    deja de seguir el numero maximo de usuarios. Solo usuario
                        que fue seguido por el script será dejado de seguir. El orden
                        es del más antiguo al más nuevo. Puede ser un número (Ej. 100)
                        o un rango (Ej. 100-200).
  --unfollow-non-followers 100-200
                        deja de seguir el numero maximo de usuarios, que no
                        te siguen de vuelta. Solo usuario que fue seguido por el script
                        será dejado de seguir. El orden es del más antiguo al
                        más nuevo. Puede ser un número (Ej. 100) o un rango (Ej. 100-200).
  --unfollow-any 100-200
                        deja de seguir el numero maximo de usuarios. El orden es
                        del más antiguo al más nuevo. Puede ser un número
                        (Ej. 100) o un rango (Ej. 100-200).
  --min-following 100   cantidad mínima de usuarios seguidos, después de alcanzar
                        esta cantidad, unfollow se detiene.
  --device 2443de990e017ece
                        identificador de dispositivo. Debe usarse solo cuando hay varios
                        dispositivos conectados a la vez.
  --old                 agregue esta bandera para usar la versión anterior de uiautomator.
                        Úselo solo si tiene problemas con la versión estándar.
  --remove-mass-followers 10
                        Elimina el número dado de seguidores de masa de la lista
                        de tus seguidores. Los "seguidores de masa" son aquellos que tienen
                        más de N usuarios seguidos, donde N se puede establecer 
                        mediante --max-following.
  --max-following 1000  Debe usarse junto con --remove-mass-followers.
                        Especifica el número de usuarios seguidos para cualquier
                        seguidor, 1000 por defecto.
```

### FAQ
- ¿Cómo detener el script? _Ctrl + C (control + C para Mac)_

- ¿Puedo evitar que mi teléfono se quede dormido? Si. Configuración -> Opciones para desarrolladores -> Stay awake.

- ¿Qué hacer si tengo un soft ban (no puedo dar me gusta / seguir / comentar)? <br/> _Borrar los datos de la aplicación de Instagram. Tendrá que iniciar sesión nuevamente y luego funcionará como de costumbre. Pero es **muy recomendable** reducir el número de interacciones para el futuro y hacer una pausa con el script._

- [¿Cómo conectar un teléfono Android a través de WiFi?](https://www.patreon.com/posts/conecte-los-de-43142649)

- [¿Cómo ejecutar en 2 o más dispositivos a la vez?](https://www.patreon.com/posts/script-en-al-43143381)

- [Script crash con **OSError: RPC server not started!** o **ReadTimeoutError**](https://www.patreon.com/posts/problemas-con-la-43147131)


### Recursos extras
Todas las funciones principales de este proyecto son de uso gratuito. Pero es posible que desee obtener un control más detallado sobre el bot a través de estas funciones:
- **Filtrando** - salta cuentas no deseadas por varios parámetros, [más aquí](#filtrando)
- **Eliminar seguidores de masa** - automatiza la "limpieza" de tu cuenta
- **Herramienta de Análisis** - crear una presentación que muestre su crecimiento, [más aquí](#an%C3%A1lisis)
- **Scrapping (próximo lanzamiento)** - hará que las interacciones sean significativamente más seguras y rápidas

Active estas funciones apoyando a nuestro pequeño equipo en Patreon: [https://insomniac-bot.com/activate/](https://insomniac-bot.com/activate/).

### Código fuente
Dado que las funciones principales son de uso gratuito, su código está aquí en la [carpeta src](https://github.com/alexal1/Insomniac/tree/master/src). Puede ayudar a la comunidad haciendo un pull request. Se agregará a la versión empaquetada después de una revisión exitosa. Para trabajar con las fuentes, por favor
1. Clone el proyecto: `git clone https://github.com/alexal1/Insomniac.git`
2. Vaya a la carpeta Insomniac: `cd Insomniac`
3. Instalar las bibliotecas necesarias: `pip3 install -r requirements.txt`
4. Ejecure el script via `python3 -m src.insomniac`

Tenga en cuenta que el código [src](https://github.com/alexal1/Insomniac/tree/master/src) puede diferir del código empaquetado. Generalmente, el código empaquetado es más estable.

_31-10-2020: En este momento hay una gran diferencia, pero sincronizaremos la versión empaquetada y de código abierto lo antes posible._

### Filtrando
Es posible que desee ignorar los seguidores de masa (ej. > 1000 usuarios seguidos) porque lo más probable es que solo estén interesados en aumentar su audiencia. O ignorar cuentas demasiado populares (ej. > 5000 seguidores) porque ellas no te notarán. Puede hacer esto (y más) usando el filtro:

| Parámetro                 | Valor         | Descripción                                                                                            |
| ------------------------- | ------------- | ------------------------------------------------------------------------------------------------------ |
| `skip_business`           | `true/false`  | salta cuetas empresa si el valor es true                                                               |
| `skip_non_business`       | `true/false`  | salta cuentas no-empresas si el valor es true                                                          |
| `min_followers`           | 100           | salta cuentas con menos seguidores que el valor dado                                                   |
| `max_followers`           | 5000          | salta cuentas con más seguidores que el valor dado                                                     |
| `min_followings`          | 10            | salta cuentas con menos usuarios seguidos que el valor dado                                            |
| `max_followings`          | 1000          | salta cuentas con más usuarios seguidos el valor dado                                                  |
| `min_potency_ratio`       | 1             | salta cuentas con una proporción (seguidores / usuarios seguidos) menor que el valor ingresado (también se pueden usar valores decimales).|
| `follow_private_or_empty` | `true/false`  | Las cuentas privadas / vacías también tienen la oportunidad de ser seguidas si el valor es true        |

Puede leer explicaciones detalladas e instrucciones sobre cómo usarlo [en esta publicación en Patreon](https://www.patreon.com/posts/43362005) **(Por favor, únete a Patreon - Plan $ 10)**.

### Whitelist y Blacklist
**Whitelist** – afecta `--remove-mass-followers`, `--unfollow` y todas las demás acciones para dejar de seguir. Los usuarios de esta lista _nunca_ se eliminarán de tus seguidores o se dejará de seguirlos.

**Blacklist** - afecta _todas las demás acciones_. Los usuarios de esta lista se saltará de inmediato: sin interacciones ni seguimiento.

Vaya a la carpeta Insomniac y cree una carpeta con el nombre de su usuario de Instagram (o abra una existente, ya que Insomniac crea dicha carpeta cuando se inicia). Crea allí un archivo `whitelist.txt` o `blacklist.txt` (o ambos). Escriba nombres de usuario en estos archivos, un nombre de usuario por línea, sin `@`, sin comas. No olvide guardar. ¡Eso es!

### Análisis
También hay una herramienta de análisis para este bot. Es un script que crea un informe en formato PDF. El informe contiene gráficos de crecimiento de seguidores de la cuenta para diferentes períodos. Las cantidades de acciones de likes, seguir y dejar de seguir están en el mismo eje para determinar la efectividad del bot. El informe también contiene estadísticas de la duración de las sesiones para las diferentes configuraciones que ha utilizado. Todos los datos se toman del archivo `sessions.json` que se genera durante la ejecución del bot.
<img src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/analytics_sample.png">

Para obtener acceso a la herramienta de análisis, debe [unirte a Patreon - Plan $10](https://www.patreon.com/insomniac_bot).

### Recursos en progreso
- [x] Siga el porcentaje dado de usuarios interaccionado con `--follow-percentage 50`
- [x] Deja de seguir el porcentaje dado de usuarios (solo aquellos que fueron seguidos por el script) con `--unfollow 100`
- [x] Deja de seguir el porcentaje dado de usuarios no seguidores (solo aquellos que fueron seguidos por el script) con `--unfollow-non-followers 100`
- [x] Soporte para intervalos de likes y cuenta de interacciones `--likes-count 2-3`
- [x] Interacción por hashtags
- [ ] Agregar acciones aleatorias para comportarse más como un humano (ver su propio feed, stories, etc.)
- [ ] Comentar durante la interacción

### ¿Por qué Insomniac?
Ya existen herramientas de automatización de Instagram que funcionan en la versión web de Instagram o mediante la API privada de Instagram. Desafortunadamente, ambas formas se han vuelto peligrosas de usar. Las acciones del navegador son muy sospechosas ahora para el sistema de detección de bots de Instagram. Y en cuanto a la API privada, se te bloqueará para siempre si Instagram detecta que la estás usando.

Es por eso que surgió la necesidad de una solución para dispositivos móviles. Instagram no puede distinguir un bot de un humano cuando se trata de tu teléfono. Sin embargo, incluso un ser humano puede alcanzar los límites cuando usa la aplicación, así que no deje de tener cuidado. Establezca siempre `--total-likes-limit` en 300 o menos. También es mejor usar `--repeat` para actuar periódicamente durante 2-3 horas, porque Instagram realiza un seguimiento de cuánto tiempo funciona la aplicación.

### Comunidad
Tenemos [Discord server](https://discord.gg/59pUYCw) que es el lugar más conveniente para discutir todos los errores, nuevas funciones, límites de Instagram, etc. Si no está familiarizado con Discord, también puede unirse a nuestro [Telegram chat](https://t.me/insomniac_chat). Y finalmente, toda la información útil se publica en nuestra [página Patreon](https://www.patreon.com/insomniac_bot). La mayoría de las publicaciones están disponibles para todos.

<p>
  <a href="https://discord.gg/59pUYCw">
    <img hspace="3" alt="Discord Server" src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/discord.png" height=84/>
  </a>
  <a href="https://t.me/insomniac_chat">
    <img hspace="3" alt="Telegram Chat" src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/telegram.png" height=84/>
  </a>
  <a href="https://www.patreon.com/insomniac_bot">
    <img hspace="3" alt="Patreon Page" src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/patreon.png" height=84/>
  </a>
</p>
