# Configuração de Mídias

## 📋 Visão Geral

Este diretório contém arquivos JSON de configuração que definem quais vídeos e podcasts estão disponíveis para cada módulo da aplicação.

## 🎯 Como Funciona

1. **Adicione arquivos de mídia** no servidor (desenvolvimento ou produção):
   - Vídeos em: `[mediasBasePath]/[caminho]/video/`
   - Áudios em: `[mediasBasePath]/[caminho]/audio/`

2. **Atualize o arquivo JSON** correspondente neste diretório

3. **A aplicação carrega automaticamente** apenas os arquivos listados no JSON

## 📁 Estrutura do JSON

```json
{
  "bibliografias": [
    {
      "bibliografiaId": 1,
      "bibliografiaTitulo": "Nome da Bibliografia",
      "caminho": "modulo\\subpasta",
      "capitulos": [
        {
          "id": 1,
          "titulo": "Título do Capítulo",
          "descricao": "Descrição opcional",
          "videoPath": "arquivo.mp4",
          "audioPath": "arquivo.mp3",
          "duracao": "45:30",
          "ordem": 1
        }
      ]
    }
  ]
}
```

## 📝 Exemplo: geopolitica-media.json

### Estrutura de Arquivos no Servidor

**Desenvolvimento:**
```
C:\Users\guilh\projeto\www\midias\
└── geopolitica\
    └── vinganca-geografia\
        ├── video\
        │   ├── capX.mp4
        │   ├── capXI.mp4
        │   └── capXII.mp4
        └── audio\
            ├── podcast_capX.mp3
            ├── podcast_capXI.mp3
            └── podcast_capXII.mp3
```

**Produção:**
```
/var/www/arquivos/
└── geopolitica/
    └── vinganca-geografia/
        ├── video/
        │   ├── capX.mp4
        │   ├── capXI.mp4
        │   └── capXII.mp4
        └── audio/
            ├── podcast_capX.mp3
            ├── podcast_capXI.mp3
            └── podcast_capXII.mp3
```

### Configuração no JSON

```json
{
  "bibliografias": [
    {
      "bibliografiaId": 1,
      "bibliografiaTitulo": "A Vingança da Geografia",
      "caminho": "geopolitica\\vinganca-geografia",
      "capitulos": [
        {
          "id": 1,
          "titulo": "Capítulo X",
          "videoPath": "capX.mp4",
          "audioPath": "podcast_capX.mp3",
          "ordem": 1
        },
        {
          "id": 2,
          "titulo": "Capítulo XI",
          "videoPath": "capXI.mp4",
          "audioPath": "podcast_capXI.mp3",
          "ordem": 2
        },
        {
          "id": 3,
          "titulo": "Capítulo XII",
          "videoPath": "capXII.mp4",
          "audioPath": "podcast_capXII.mp3",
          "ordem": 3
        }
      ]
    }
  ]
}
```

## 🔧 Campos Disponíveis

### Bibliografia
- `bibliografiaId` (obrigatório): ID único da bibliografia
- `bibliografiaTitulo` (opcional): Título da bibliografia
- `caminho` (obrigatório): Caminho relativo dentro de mediasBasePath (use `\\` para Windows em dev)
- `capitulos` (obrigatório): Array de capítulos

### Capítulo
- `id` (obrigatório): ID único do capítulo
- `titulo` (obrigatório): Título do capítulo
- `descricao` (opcional): Descrição detalhada
- `videoPath` (opcional): Nome do arquivo de vídeo (MP4)
- `audioPath` (opcional): Nome do arquivo de áudio (MP3/WAV)
- `duracao` (opcional): Duração no formato "HH:MM:SS" ou "MM:SS"
- `ordem` (opcional): Ordem de exibição (número)

## ⚠️ Notas Importantes

1. **Apenas arquivos no JSON são carregados**: Se um arquivo existe no servidor mas não está no JSON, não será exibido

2. **Caminhos relativos**: Use apenas o nome do arquivo em `videoPath` e `audioPath`. O caminho completo é construído automaticamente

3. **Separador de diretório**: 
   - Desenvolvimento (Windows): Use `\\` no campo `caminho`
   - Produção (Linux): Será convertido automaticamente para `/`

4. **Campos opcionais**: 
   - Um capítulo pode ter só vídeo, só áudio, ou ambos
   - `descricao` e `duracao` são opcionais mas recomendados

5. **Formato de vídeo**: Recomendado MP4 (H.264) para compatibilidade
6. **Formato de áudio**: MP3 ou WAV

## 🔄 Como Adicionar Novos Arquivos

1. **Copie os arquivos** para o diretório correto no servidor
2. **Edite o arquivo JSON** correspondente
3. **Adicione a entrada** do novo capítulo
4. **Salve o arquivo**
5. **Recarregue a página** da aplicação

A aplicação irá carregar automaticamente a nova configuração!

## 📊 Criar Novo Módulo

Para criar configuração de um novo módulo (ex: história):

1. Crie arquivo: `historia-media.json`
2. Use a mesma estrutura do exemplo
3. No componente, carregue com: `mediaConfigService.carregarConfigMedia('historia')`

## 🐛 Troubleshooting

### Vídeos não aparecem
- ✅ Verifique se o JSON está bem formatado (use um validador JSON online)
- ✅ Confirme que o `caminho` está correto
- ✅ Verifique se os nomes dos arquivos correspondem exatamente
- ✅ Confira o console do navegador para erros

### Erro ao carregar configuração
- ✅ Verifique se o arquivo JSON está em `public/assets/media-config/`
- ✅ Confirme que o nome do arquivo segue o padrão: `[modulo]-media.json`
- ✅ Certifique-se de que o JSON é válido

### Players não funcionam
- ✅ Verifique o formato dos arquivos (MP4 para vídeo, MP3/WAV para áudio)
- ✅ Confirme que os arquivos estão acessíveis no servidor
- ✅ Teste os caminhos diretamente no navegador

