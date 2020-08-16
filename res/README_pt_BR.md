<img align="left" width="80" height="80" src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/icon.jpg" alt="Insomniac">

# Insomniac
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/alexal1/Insomniac?label=latest%20version)
![Python](https://img.shields.io/badge/built%20with-Python3-red.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)

[inglês](https://github.com/alexal1/Insomniac/blob/master/README.md) | [espanhol](https://github.com/alexal1/Insomniac/blob/master/res/README_es.md)

Like e seguir automaticamente no seu celular/tablet Android. Não é necessário root: Funciona com [UI Automator](https://developer.android.com/training/testing/ui-automator), que é uma estrutura oficial de teste de interface do usuário do Android.

<img src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/demo.gif">

### Como instalar
1. Clone o projeto: `git clone https://github.com/alexal1/Insomniac.git`
2. Instale [uiautomator](https://github.com/xiaocong/uiautomator) e [colorama](https://pypi.org/project/colorama/): `pip3 install uiautomator colorama`
3. Download e unzip [Android platform tools](https://developer.android.com/studio/releases/platform-tools), mova-os para um diretório em que você não os excluirá acidentalmente, por exemplo:
```
mkdir -p ~/Library/Android/sdk
mv <caminho-para-downloads>/platform-tools/ ~/Library/Android/sdk
```
4. [Add o caminho do platform-tools às variáveis de ambiente do sistema](https://github.com/alexal1/Insomniac/wiki/Add-o-caminho-do-platform-tools-as-variaveis-de-ambiente-do-sistema-pt_BR). Se você fizer isso corretamente, o comando `adb devices` no terminal(prompt de comando) imprimirá `List of devices attached`

### Como instalar no Raspberry Pi OS
1. Update apt-get: `sudo apt-get update`
2. Instale ADB e Fastboot: `sudo apt-get install -y android-tools-adb android-tools-fastboot`
3. Clone o projeto: `git clone https://github.com/alexal1/Insomniac.git`
4. Instale [uiautomator](https://github.com/xiaocong/uiautomator) e [colorama](https://pypi.org/project/colorama/): `pip3 install uiautomator colorama`

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
```
cd <camimho-do-projeto>/Insomniac
python3 insomniac.py --interact <username1> <username2> ...
```
Verifique se a tela está ligada e se o dispositivo está desbloqueado. Você não precisa abrir o aplicativo do Instagram, o script o abre e fecha quando terminar. Apenas verifique se o aplicativo Instagram está instalado. Se tudo estiver bem, o script abrirá os seguidores de cada blogueiro e dará like em suas postagens.

### Uso
Lista completa de argumentos da linha de comando:
```
  --interact username1 [username2 ...]
                        lista de usernames com seguidores que você deseja
                        interagir
  --likes-count 2       número de likes para cada usuário interagido, 2 por padrão
  --total-likes-limit 300
                        limite na quantidade total de likes durante a sessão, 300
                        por padrão
  --interactions-count 70
                        número de interações por cada blogueiro, 70 por
                        padrão. Somente interações bem-sucedidas contam
  --repeat 180          repita a mesma sessão novamente após N minutos depois de
                        completada, desativada por padrão
  --follow-percentage 50
                        seguir determinada porcentagem de usuários interagidos, 0 por
                        padrão
  --follow-limit 50     limite na quantidade de seguidores durante a interação com
                        os seguidores de cada blogueiro, desativado por padrão
  --unfollow 100        deixar de seguir o número máximo de usuários. Somente usuários
                        seguidos por este script serão deixados de seguir. A ordem
                        é do seguidor mais antigo para o mais novo
  --unfollow-non-followers 100
                        deixar de seguir o número máximo de usuários, que não
                        te seguem de volta. Somente usuários seguidos por este script
                        serão deixados de seguir. A ordem é do seguidor mais antigo para
                        o mais novo
  --unfollow-any 100    deixar de seguir o número máximo de usuários. A ordem é
                        do seguidor mais antigo para o mais novo
  --min-following 100   número mínimo de seguidores, após atingir
                        este valor, unfollow se detém
  --device 2443de990e017ece
                        identificador de dispositivo. Deve ser usado apenas quando vários
                        dispositivos estão conectados de uma só vez
```

### FAQ
- Posso impedir que meu telefone adormeça? Sim. Ajustes -> Opções de desenvolvedor -> Permanecer ativo.
- [Como conectar um telefone Android via WiFi?](https://www.patreon.com/posts/connect-android-38655552)
- [Como rodar em 2 ou mais dispositivos ao mesmo tempo?](https://www.patreon.com/posts/38683736)
- [Script quebra com **OSError: RPC server not started!** ou **ReadTimeoutError**](https://www.patreon.com/posts/problems-with-to-38702683)
- [As contas privadas são sempre ignoradas. Como segui-las também?](https://www.patreon.com/posts/enable-private-39097751) **(Por favor, juntar-se ao Patreon - Plano $ 10)**
- [Filtrar por contagem de seguidores / seguidores, ratio, business / não business](https://www.patreon.com/posts/38826184) **(Por favor, juntar-se ao Patreon - Plano $ 10)**

### Análises 
Também existe uma ferramenta de análise para este bot. É um script que cria um relatório em formato PDF. O relatório contém gráficos de crescimento de seguidores da conta para diferentes períodos. Likes, seguir e deixar de seguir as ações estão no mesmo eixo para determinar a eficácia do bot. O relatório também contém estatísticas da duração das sessões para diferentes configurações que você usou. Todos os dados são retirados do `sessions.json` arquivo gerado durante a execução do bot.
<img src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/analytics_sample.png">

Para ter acesso à ferramenta de análise, você precisa [juntar-se ao Patreon - Plano $ 10](https://www.patreon.com/insomniac_bot).

### Recursos em progresso
- [x] Seguir determinada porcentagem de usuários interagidos com `--follow-percentage 50`
- [x] Deixar de seguir um determinado número de usuários (somente aqueles que foram seguidos pelo script) com `--unfollow 100`
- [x] Deixar de seguir um determinado número de não seguidores (somente aqueles que foram seguidos pelo script) com `--unfollow-non-followers 100`
- [ ] Add ações aleatórias para se comportar mais como um humano (assistir seu próprio feed, stories, etc.)
- [ ] Suportar intervalos para likes e contagem de interações como `--likes-count 2-3`
- [ ] Interação por hashtags
- [ ] Comentar durante a interação

### Por que Insomniac?
Já existe [InstaPy](https://github.com/timgrossmann/InstaPy), que trabalha com o a versão do Instagram web. Infelizmente, ações no navegador tornaram-se muito suspeitas para o sistema de detecção de bots do Instagram. Agora, o InstaPy e scripts semelhantes funcionam no máximo uma hora, o Instagram bloqueia a possibilidade de executar qualquer ação e, se você continuar usando o InstaPy, isso poderá banir sua conta.

É por isso que surgiu a necessidade de uma solução para dispositivos móveis. O Instagram não pode distinguir bot de um humano quando se trata do seu telefone. No entanto, mesmo um ser humano pode atingir limites ao usar o aplicativo, portanto, não deixe de ter cuidado. Sempre defina `--total-likes-limit` para 300 ou menos. Também é melhor usar `--repeat` para repetir periodicamente por 2-3 horas, porque o Instagram acompanha por quanto tempo o aplicativo funciona.

### Comunidade
Temos o [Discord server](https://discord.gg/59pUYCw) qual é o lugar mais conveniente para discutir todos os bugs, novos recursos, limites do Instagram etc. Se você não está familiarizado com o Discord, também pode se juntar ao nosso [Telegram chat](https://t.me/insomniac_chat). E, finalmente, todas as informações úteis são publicadas em nosso [Patreon page](https://www.patreon.com/insomniac_bot). A maioria das postagens está disponível para todos, mas algumas exigem o Plano $ 10: Esta é a nossa maneira de continuar evoluindo e melhorando o bot.

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

