# Mapa de teste: Praça Tiradentes → Cavalo Babão (RPG Maker MZ)

Mapa *parallax* (desenhado) de 25×40 tiles (1200×1920 px), inspirado no trajeto real em Curitiba.
O layout é simplificado para jogo, não é uma planta exata.

- **Início:** porta da Catedral Basílica, na Praça Tiradentes (tile 12,10).
- **Caminho:** praça com petit-pavé, Marco Zero e vitrine do calçamento antigo → rua → Rua Claudino dos Santos (casario histórico).
- **Fim:** Largo da Ordem, chafariz do **Cavalo Babão** (interagir com ele encerra o teste e volta ao título).

## Arquivos
| Arquivo | Para onde vai no seu projeto |
|---|---|
| `img/parallaxes/!praca_tiradentes.png` | `img/parallaxes/` (chão do mapa) |
| `img/parallaxes/!praca_tiradentes_topo.png` | `img/parallaxes/` (copas e postes, desenhados acima do personagem) |
| `js/plugins/MapaParalaxe.js` | `js/plugins/` |
| `data/Map002.json` | `data/` (veja o passo 2) |
| `fonte/*.svg` | arte original, para editar |

O `!` no nome faz a imagem rolar junto com o mapa (regra do próprio RPG Maker).

## Instalação
1. Copie as pastas `img` e `js` para dentro da pasta do seu projeto.
2. No editor, crie um **mapa novo** (botão direito na lista de mapas → *Novo*) e salve o projeto.
   Se o seu projeto só tinha o `MAP001`, ele vira o `MAP002`. **Feche o RPG Maker** e copie
   `data/Map002.json` por cima do arquivo de mesmo nome. Se o número for outro, renomeie o arquivo
   (ex.: `Map003.json`) antes de copiar.
3. Reabra o projeto. Em *Ferramentas → Gerenciador de Plugins*, adicione e ative **MapaParalaxe**.
4. No mapa, clique com o botão direito no tile **(12,10)**, logo abaixo da porta da catedral, e escolha
   *Definir posição inicial → Jogador*.
5. Teste (F5 ou *Jogar teste*).

## Como funciona
- **Colisão:** a **região 1** (camada de regiões, tecla F7 no editor) marca o que é bloqueado. O resto é passável.
  Para ajustar, pinte ou apague a região 1 no editor.
- **Camada superior:** a nota do mapa tem `<topo: !praca_tiradentes_topo>`, e o plugin desenha essa imagem acima dos personagens.
- **Eventos:** placa da catedral, Marco Zero, vitrine do calçamento e Cavalo Babão (fim). Edite à vontade.
- Não há música definida, para não depender de arquivos de áudio. Escolha uma em *Propriedades do mapa*.

## Regerar a arte
`python3 tools/gerar_mapa_tiradentes.py` (precisa de Python 3, Node e Playwright).
