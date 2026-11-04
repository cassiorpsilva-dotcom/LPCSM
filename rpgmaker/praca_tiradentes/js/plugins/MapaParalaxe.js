/*:
 * @target MZ
 * @plugindesc Mapas de paralaxe: colisão por região e camada acima do personagem.
 * @author LPCSM
 * @help MapaParalaxe.js
 * Nas notas do mapa:
 *   <paralaxe>          ativa o modo paralaxe: tudo é passável, exceto região 1.
 *   <topo: arquivo>     imagem de img/parallaxes desenhada ACIMA dos personagens
 *                       (copas de árvores, cabeças de poste...), presa ao mapa.
 * Use um nome de paralaxe começando com "!" para a imagem rolar junto com o mapa.
 */
(() => {
  const ehParalaxe = () => $dataMap && /<paralaxe>/i.test($dataMap.note || "");

  const _checkPassage = Game_Map.prototype.checkPassage;
  Game_Map.prototype.checkPassage = function(x, y, bit) {
    if (ehParalaxe()) return this.regionId(x, y) !== 1;
    return _checkPassage.call(this, x, y, bit);
  };

  const _createTilemap = Spriteset_Map.prototype.createTilemap;
  Spriteset_Map.prototype.createTilemap = function() {
    _createTilemap.call(this);
    const m = ehParalaxe() && /<topo:\s*([^>]+)>/i.exec($dataMap.note);
    if (m) {
      this._topoParalaxe = new Sprite(ImageManager.loadParallax(m[1].trim()));
      this._topoParalaxe.z = 9;
      this._tilemap.addChild(this._topoParalaxe);
    }
  };

  const _update = Spriteset_Map.prototype.update;
  Spriteset_Map.prototype.update = function() {
    _update.call(this);
    if (this._topoParalaxe) {
      this._topoParalaxe.x = Math.round(-$gameMap.displayX() * $gameMap.tileWidth());
      this._topoParalaxe.y = Math.round(-$gameMap.displayY() * $gameMap.tileHeight());
    }
  };
})();
