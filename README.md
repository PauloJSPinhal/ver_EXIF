# Ver EXIF

Visualizador EXIF completo com interface gráfica nativa (GTK3) para imagens, integrado ao Nautilus.

## 📂 Estrutura de Configuração

O script utiliza uma pasta de configuração em `~/.config/ver-exif/` para armazenar:
- `tag-dictionary.json` - Dicionário personalizado com descrições e categorias das tags
- `favorites.json` - Lista de metadados favoritos

### Como salvar a pasta `ver-exif` em `.config`

Para copiar a pasta de configuração para o diretório correto:

```bash
# Copiar a pasta ver-exif para ~/.config/
cp -r ver-exif ~/.config/

# Ou se estiver no diretório atual:
mv ver-exif ~/.config/
```

A estrutura final deve estar em:
```
~/.config/ver-exif/
├── tag-dictionary.json
└── favorites.json
```

## Descrição

Este script permite visualizar os metadados EXIF de imagens através de uma interface gráfica GTK3 avançada. Ele é projetado para ser usado como script do Nautilus no ambiente GNOME, herdando automaticamente as variáveis de ambiente do sistema (GTK_THEME, GSETTINGS_BACKEND, DBUS_SESSION_BUS_ADDRESS, etc.).

## Requisitos

- Python 3
- GTK3 (via gi.repository)
- `exiftool` (libimage-exiftool-perl)
- Nautilus (GNOME Files)

## Instalação

1. Instale o `exiftool` (necessário para leitura completa de metadados):
   ```bash
   sudo apt install libimage-exiftool-perl
   ```

2. Copie o arquivo `ver-exif.py` para a pasta de scripts do Nautilus:
   ```bash
   mkdir -p ~/.local/share/nautilus/scripts/
   cp ver-exif.py ~/.local/share/nautilus/scripts/
   chmod +x ~/.local/share/nautilus/scripts/ver-exif.py
   ```

3. Reinicie o Nautilus ou faça logout/relogin.

## Uso

1. Abra o Nautilus
2. Selecione uma imagem
3. Clique com o botão direito e escolha "Scripts" → "Ver EXIF"

## Funcionalidades

- **Visualização estruturada** dos metadados com categorias e sub-categorias:
  - 📷 EXIF Padrão, MakerNotes, XMP, IPTC, Composite, File, GPS, ICC
  - Sub-categorias inteligentes (Ex: "📷 Corpo & Fabricante", "⚡ Exposição & Disparo", etc.)
- **Busca em tempo real** para filtrar tags, valores e categorias
- **Exportação** para JSON ou CSV (com indicação de favoritos)
- **Menu de contexto** para adicionar/remover metadados dos favoritos
- **Expandir/recolher** toda a árvore de metadados
- **Dicionário personalizável** (`tag-dictionary.json`) para descrições e categorias
- **Sistema de favoritos** para marcar tags importantes
- Suporte a metadados complexos (MakerNotes, XMP, IPTC, ICC Profile)
- Formatação automática de valores e truncamento para valores longos
- Tooltips com descrições das tags

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE.md](LICENSE.md) para mais detalhes.

## Changelog

Veja o arquivo [CHANGELOG.md](CHANGELOG.md) para informações sobre versões e alterações.
