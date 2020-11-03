<img align="left" width="80" height="80" src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/icon.jpg" alt="Insomniac">

# Insomniac
![PyPI](https://img.shields.io/pypi/v/insomniac?label=latest%20version)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/insomniac)
![PyPI - Downloads](https://img.shields.io/pypi/dm/insomniac)

[inglês](https://github.com/alexal1/Insomniac/blob/master/README.md) | [espanhol](https://github.com/alexal1/Insomniac/blob/master/res/README_es.md)

Like e seguir automaticamente no seu celular/tablet Android. Não é necessário root: Funciona com [UI Automator](https://developer.android.com/training/testing/ui-automator), que é uma estrutura oficial de teste de interface do usuário do Android.

<img src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/demo.gif">

### Índice
- [Por que você deve automatizar a atividade do Instagram  (likes, seguir, etc.)?](#por-que-voc%C3%AA-deve-automatizar-a-atividade-do-instagram--likes-seguir-etc)
- [Como instalar](#como-instalar)
    * [Como instalar no Raspberry Pi OS](#como-instalar-no-raspberry-pi-os)
- [Começando](#começando)
    * [Exemplo de uso](#exemplo-de-uso)
    * [Lista completa de argumentos da linha de comando](#lista-completa-de-argumentos-da-linha-de-comando)
    * [FAQ](#faq)
- [Recursos extras](#recursos-extras)
- [Código fonte](#código-fonte)
- [Filtrando](#filtrando)
- [Whitelist e Blacklist](#whitelist-e-blacklist)
- [Análises](#análises)
- [Recursos em progresso](#recursos-em-progresso)
- [Por que Insomniac?](#por-que-insomniac)
- [Comunidade](#comunidade)

### Por que você deve automatizar a atividade do Instagram  (likes, seguir, etc.)?
💸 Se você quer apenas _aumentar_ sua contagem de seguidores ou obter mais curtidas, há um monte de empresas que lhe darão isso imediatamente por alguns $$$. Mas muito provavelmente seu público será de bots e seguidores de massa.

🌱 Se você deseja obter seguidores engajados, que estarão interessados em seu conteúdo e provavelmente pagarão por seus serviços, então a _automação_ é o caminho certo.

🎯 Este bot do Instagram fornece métodos para **atingir** o público que provavelmente está interessado **em você**. Esses métodos são:
1. Interaja com seguidores de **blogueiro(a)s** com conteúdo semelhante
2. Interaja com quem gosta de **hashtags** que você usa
3. **Filtre** contas para evitar bots e seguidores de massa

📈 Usar todos esses métodos dá o melhor resultado.

### Como instalar
1. Instale o pacote **insomniac**: execute `python3 -m pip install insomniac` no terminal / Prompt de comando<br/><sub><sup>Desde que **python** e **pip** já estejam instalados. Aprenda <a href="https://github.com/alexal1/Insomniac/wiki/Install-Python">a verificar isso</a>.</sup></sub>
2. Salve o arquivo [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) para um diretório de onde você iniciará o script (clique com o botão direito no link e, em seguida, Salvar link como / Salvar)
3. Download e unzip [Android platform tools](https://developer.android.com/studio/releases/platform-tools), mova-os para um diretório em que você não os excluirá acidentalmente. O Lugar padrão é `C:\android-sdk\` (Windows), `~/Library/Android/sdk` (Linux/macOS)
4. [Add o caminho do platform-tools às variáveis de ambiente do sistema](https://github.com/alexal1/Insomniac/wiki/Add-o-caminho-do-platform-tools-as-variaveis-de-ambiente-do-sistema-pt_BR). Se você fizer isso corretamente, o comando `adb devices` no terminal(prompt de comando) imprimirá `List of devices attached`

### Como instalar no Raspberry Pi OS
1. Update apt-get: `sudo apt-get update`
2. Instale ADB e Fastboot: `sudo apt-get install -y android-tools-adb android-tools-fastboot`
3. Instale o pacote **insomniac**: execute `python3 -m pip install insomniac` no terminal
4. Salve o arquivo [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) para um diretório de onde você iniciará o script (clique com o botão direito no link e, em seguida, Salvar link como / Salvar)

_IMPORTANTE: se você já usou a v2.x.x, o arquivo insomniac.py entrará em conflito com o pacote insomniac. Portanto, salve start.py em uma pasta diferente_

### Começando
1. Conecte o dispositivo Android ao seu computador com um cabo USB
2. Habilitar [Opções de desenvolvedor](https://developer.android.com/studio/debug/dev-options?hl=pt-br) no seu dispositivo
>No Android 4.1 e inferior, a tela de opções do desenvolvedor está disponível por padrão. No Android 4.2 e superior, você deve ativar esta tela. Para ativar as opções do desenvolvedor, toque na opção Número da compilação 7 vezes. Você pode encontrar esta opção em um dos seguintes locais, dependendo da sua versão do Android:
>
> Android 9 (API level 28) e superior: Ajustes > Sobre o telefone > Número de montagem
>
> Android 8.0.0 (API level 26) e Android 8.1.0 (API level 26): Ajustes > Sistema > Sobre o telefone > Número de montagem
>
> Android 7.1 (API level 25) e inferior: Ajustes > Sobre o telefone > Número de montagem
3. Ative a **depuração USB** (e **instalar aplicativos via USB**, se houver essa opção) na tela de opções de desenvolvedor.
4. O dispositivo solicitará que você permita a conexão do computador. Pressione "Permitir"
5. Escreva `adb devices` no terminal. Ele exibirá dispositivos conectados. Deve haver exatamente um dispositivo. Em seguida, execute o script (funciona em Python 3):
6. Abra o Terminal(prompt de comando) na pasta com o arquivo baixado [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) (ou digite `cd <camimho-para-start.py>`) e execute
```
python3 start.py --interact @natgeo
```
Verifique se a tela está ligada e se o dispositivo está desbloqueado. Você não precisa abrir o aplicativo do Instagram, o script o abre e fecha quando terminar. Apenas verifique se o aplicativo Instagram está instalado. Se tudo estiver bem, o script abrirá os seguidores do `@netgeo` e dará like em suas postagens.

### Exemplo de uso
Digamos que você tenha um blog de viagens. Então você pode querer usar essa configuração:
```
python3 start.py --interact @natgeo amazingtrips beautifuldestinations --interactions-count 20-30 --likes-count 1-3 --follow-percentage 20 --repeat 120-180
```
O script irá interagir sequencialmente com 20-30 seguidores do `@natgeo`, 20-30 curtidores de posts `#amazingtrips`, e 20-30 curtidores de posts `#beautifuldestinations`. Durante cada interação, ele gostará de 1-3 postagens aleatórias e também seguirá 20% dos usuários interagidos. Depois de concluído, ele fechará o aplicativo do Instagram e aguardará 120-180 minutos. Então o script vai repetir o mesmo (e vai se repetir infinitamente), mas os usuários já interagidos serão ignorados. A lista de fontes (`@natgeo`, `#amazingtrips` e `#beutifuldestinations`) será embaralhada a cada vez.

Toda essa aleatoriedade torna muito difícil para o Instagram detectar que você está usando um bot. Porém, tome cuidado com o número de interações, pois até mesmo um humano pode ser banido por violar os limites.

### Lista completa de argumentos da linha de comando
Você também pode ver esta lista executando sem argumentos: `python3 start.py`.
```
  --interact hashtag [@usuario ...]
                        lista de hashtag e usuários. Os usuários devem começar
                        com o símbolo "@". O script irá interagir com curtidores
                        de postagens que tenham hashtags e com seguidores de usuários
  --likes-count 2-4     número de likes para cada usuário interagido, 2 por padrão.
                        Pode ser um número (por exemplo, 2) ou um intervalo
                        (por exemplo 2-4).
  --total-likes-limit 300
                        limite na quantidade total de likes durante a sessão, 300
                        por padrão.
  --interactions-count 60-80
                        número de interações por cada blogueiro, 70 por
                        padrão. Pode ser um número (por exemplo, 70)
                        ou um intervalo (por exemplo 60-80). Somente 
                        interações bem-sucedidas contam.
  --repeat 120-180      repita a mesma sessão novamente após N minutos depois de
                        completada, desativada por padrão. Pode ser um número em
                        minutos (por exemplo, 180) ou um intervalo (por exemplo, 120-180).
  --follow-percentage 50
                        seguir determinada porcentagem de usuários interagidos, 0 por
                        padrão
  --follow-limit 50     limite na quantidade de seguidores durante a interação com
                        os seguidores de cada blogueiro, desativado por padrão
  --unfollow 100-200    deixar de seguir o número máximo de usuários. Somente usuários
                        seguidos por este script serão deixados de seguir. A ordem
                        é do seguidor mais antigo para o mais novo. Pode ser um
                        número (por exemplo, 100) ou um intervalo (por exemplo, 100-200).
  --unfollow-non-followers 100-200
                        deixar de seguir o número máximo de usuários, que não
                        te seguem de volta. Somente usuários seguidos por este script
                        serão deixados de seguir. A ordem é do seguidor mais antigo para
                        o mais novo. Pode ser um número (por exemplo, 100) ou um
                        intervalo (por exemplo, 100-200).
  --unfollow-any 100-200
                        deixar de seguir o número máximo de usuários. A ordem é
                        do seguidor mais antigo para o mais novo. Pode ser um
                        número (por exemplo, 100) ou um intervalo (por exemplo, 100-200).
  --min-following 100   número mínimo de usuários seguidos, após atingir
                        este valor, unfollow se detém
  --device 2443de990e017ece
                        identificador de dispositivo. Deve ser usado apenas quando vários
                        dispositivos estão conectados de uma só vez
  --old                 adicione este sinalizador para usar a versão antiga do uiautomator.
                        Use-o apenas se tiver problemas com a versão padrão
  --remove-mass-followers 10
                        Remova determinado número de seguidores de massa da lista de
                        seus seguidores."Seguidores de massa" são aqueles que têm mais
                        de N usuários seguidos, onde N pode ser definido via --max-following
  --max-following 1000  Deve ser usado junto com --remove-mass-followers.
                        Especifica o número máximo de usuários seguidos para qualquer
                        seguidor, 1000 por padrão
```

### FAQ
- Como parar o script? _Ctrl + C (control + C para Mac)_

- Posso impedir que meu telefone adormeça? Sim. Ajustes -> Opções de desenvolvedor -> Permanecer ativo.

- O que fazer se eu receber um soft ban (não posso curtir / seguir / comentar)?<br/>_Limpe os dados do aplicativo Instagram. Você terá que fazer o login novamente e então tudo funcionará normalmente. Mas é **altamente recomendado** diminuir sua contagem de interações para o futuro e fazer uma pausa com o script._

- [Como conectar um telefone Android via WiFi?](https://www.patreon.com/posts/translate-s-via-43142420)

- [Como rodar em 2 ou mais dispositivos ao mesmo tempo?](https://www.patreon.com/posts/translate-script-43143216)

- [Script quebra com **OSError: RPC server not started!** ou **ReadTimeoutError**](https://www.patreon.com/posts/problemas-com-o-43143768)

### Recursos extras
Todos os recursos principais neste projeto são de uso gratuito. Mas você pode querer obter um controle mais refinado sobre o bot por meio destes recursos:
- **Filtrando** - pular contas indesejadas por vários parâmetros, [mais aqui](#filtrando)
- **Removendo seguidores de massa** - automatize a "limpeza" da sua conta
- **Ferramenta de análises** - construir uma apresentação que mostre seu crescimento, [mais aqui](#análises)
- **Scrapping (próximo lançamento)** - tornará as interações significativamente mais seguras e rápidas

Ative esses recursos apoiando nossa pequena equipe no Patreon: [https://insomniac-bot.com/activate/](https://insomniac-bot.com/activate/).

### Código fonte
Uma vez que os recursos principais são de uso gratuito, seus códigos estão aqui na [pasta src](https://github.com/alexal1/Insomniac/tree/master/src). Você pode ajudar a comunidade fazendo um pull request. Ele será adicionado à versão empacotada após revisão bem-sucedida. Para trabalhar com as fontes, por favor
1. Clone o projeto: `git clone https://github.com/alexal1/Insomniac.git`
2. Vá para a pasta Insomniac: `cd Insomniac`
3. Instale as bibliotecas necessárias: `pip3 install -r requirements.txt`
4. Execute o script via `python3 -m src.insomniac`

Observe que o código [src](https://github.com/alexal1/Insomniac/tree/master/src) pode ser diferente do código empacotado. Geralmente, o código empacotado é mais estável.


_31-10-2020: No momento, há uma grande diferença, mas vamos sincronizar a versão empacotada e a versão de código aberto o mais rápido possível._

### Filtrando
Você pode querer ignorar os seguidores em massa (ex: seguindo > 1000 usuários) porque eles provavelmente estão interessados apenas em aumentar seu público. Ou ignore contas muito populares (ex: > 5000 seguidores) porque eles não vão notar você. Você pode fazer isso (e muito mais) usando o filtro:

| Parâmetro                 | Valor         | Descrição                                                                                              |
| ------------------------- | ------------- | ------------------------------------------------------------------------------------------------------ |
| `skip_business`           | `true/false`  | pula contas empresa se for true.                                                                       |
| `skip_non_business`       | `true/false`  | pula contas não-empresa se for true.                                                                   |
| `min_followers`           | 100           | pula contas com menos seguidores do que o valor dado.                                                  |
| `max_followers`           | 5000          | pula contas com mais seguidores do que o valor dado.                                                   |
| `min_followings`          | 10            | pula contas com menos usuários seguidos do que o valor dado.                                           |
| `max_followings`          | 1000          | pula contas com mais usuários seguidos do que o valor dado.                                            |
| `min_potency_ratio`       | 1             | pula contas com proporção (seguidores/usuários seguidos) menor do que o valor fornecido(valores decimais também podem ser usados).|                                                                     |
| `follow_private_or_empty` | `true/false`  | contas privadas / vazias também têm a chance de serem seguidas se for true.                            |

Você pode ler a explicação detalhada e as instruções de como usá-lo [no post Patreon](https://www.patreon.com/posts/43362005) **(Por favor, juntar-se ao Patreon - Plano $ 10)**.

### Whitelist e Blacklist
**Whitelist** – afeta `--remove-mass-followers`, `--unfollow` e todas as outras ações de deixar de seguir. Os usuários desta lista _nunca_ serão removidos de seus seguidores ou serão deixados seguir.

**Blacklist** - afeta _todas outras ações_. Os usuários desta lista serão ignorados imediatamente: sem interações e sem seguimento.

Vá para a pasta do Insomniac e crie uma pasta chamada como seu usuário do Instagram (ou abra uma existente, pois o Insomniac cria tal pasta quando iniciado). Crie lá um arquivo `whitelist.txt` ou `blacklist.txt` (ou ambos). Escreva nomes de usuário nestes arquivos, um nome de usuário por linha, sem `@`, sem vírgulas. Não se esqueça de salvar. É isso aí!

### Análises 
Também existe uma ferramenta de análise para este bot. É um script que cria um relatório em formato PDF. O relatório contém gráficos de crescimento de seguidores da conta para diferentes períodos. Likes, seguir e deixar de seguir as ações estão no mesmo eixo para determinar a eficácia do bot. O relatório também contém estatísticas da duração das sessões para diferentes configurações que você usou. Todos os dados são retirados do `sessions.json` arquivo gerado durante a execução do bot.
<img src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/analytics_sample.png">

Para ter acesso à ferramenta de análise, você precisa [juntar-se ao Patreon - Plano $ 10](https://www.patreon.com/insomniac_bot).

### Recursos em progresso
- [x] Seguir determinada porcentagem de usuários interagidos com `--follow-percentage 50`
- [x] Deixar de seguir um determinado número de usuários (somente aqueles que foram seguidos pelo script) com `--unfollow 100`
- [x] Deixar de seguir um determinado número de não seguidores (somente aqueles que foram seguidos pelo script) com `--unfollow-non-followers 100`
- [x] Suportar intervalos para likes e contagem de interações como `--likes-count 2-3`
- [x] Interação por hashtags
- [ ] Add ações aleatórias para se comportar mais como um humano (assistir seu próprio feed, stories, etc.)
- [ ] Comentar durante a interação

### Por que Insomniac?
Já existem ferramentas de automação do Instagram que funcionam tanto na versão web do Instagram quanto via API privada do Instagram. Infelizmente, as duas formas tornaram-se perigosas de usar. O sistema de detecção de bots do Instagram é rígido para as ações no navegador agora. E quanto à API privada - você será bloqueado para sempre se o Instagram detectar que você está usando.

É por isso que surgiu a necessidade de uma solução para dispositivos móveis. O Instagram não pode distinguir bot de um humano quando se trata do seu telefone. No entanto, mesmo um ser humano pode atingir os limites ao usar o aplicativo, portanto, não deixe de ter cuidado. Sempre defina `--total-likes-limit` para 300 ou menos. Também é melhor usar `--repeat` para repetir periodicamente por 2-3 horas, porque o Instagram acompanha por quanto tempo o aplicativo funciona.

### Comunidade
Temos o [Discord server](https://discord.gg/59pUYCw) qual é o lugar mais conveniente para discutir todos os bugs, novos recursos, limites do Instagram etc. Se você não está familiarizado com o Discord, também pode se juntar ao nosso [Telegram chat](https://t.me/insomniac_chat). E, finalmente, todas as informações úteis são publicadas em nosso [Patreon page](https://www.patreon.com/insomniac_bot).

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
