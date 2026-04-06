# Ver EXIF

Visualizador EXIF com interface gráfica nativa (GTK3) para imagens, integrado ao Nautilus.

## Descrição

Este script permite visualizar os metadados EXIF de imagens através de uma interface gráfica GTK3. Ele é projetado para ser usado como script do Nautilus no ambiente GNOME, herdando automaticamente as variáveis de ambiente do sistema (GTK_THEME, GSETTINGS_BACKEND, DBUS_SESSION_BUS_ADDRESS, etc.).

## Requisitos

- Python 3
- GTK3 (via gi.repository)
- Pillow (PIL)
- Nautilus (GNOME Files)

## Instalação

1. Certifique-se de ter os pacotes necessários instalados:
   ```bash
   sudo apt install python3-gi python3-pil
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

- Visualização organizada dos metadados EXIF por categorias:
  - Câmera/Equipamento
  - Configurações de Imagem
  - Data e Hora
  - GPS/Localização
  - Exposição/Disparo
  - Outros/Metadados
- Formatação automática de valores (tempo de exposição, abertura, focalização, etc.)
- Suporte a coordenadas GPS

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE.md](LICENSE.md) para mais detalhes.

## Changelog

Veja o arquivo [CHANGELOG.md](CHANGELOG.md) para informações sobre versões e alterações.
