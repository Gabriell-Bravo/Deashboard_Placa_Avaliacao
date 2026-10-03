# QR Plaquinhas — Gerenciador de QR Codes Dinâmicos

Dashboard para criar e gerenciar QR codes das plaquinhas de avaliação Google.

## Como funciona

1. Você cria um QR no painel → o sistema gera um identificador único, ex: `PLACA-8177`
2. O QR aponta para uma URL **fixa** do seu sistema: `/r/PLACA-8177`
3. Essa URL redireciona para o link do Google (ou qualquer outro)
4. Depois de impresso, você pode trocar o destino no painel sem reimprimir a placa
5. O código `PLACA-...` fica impresso **abaixo do QR** para você saber qual placa é qual
6. No dashboard: leituras, valor arrecadado, vendidas, total e disponíveis
7. Dá para marcar placa como vendida informando o valor

## Como rodar (local)

```bash
python -m pip install -r requirements.txt
python app.py
```

Abra: [http://127.0.0.1:5000](http://127.0.0.1:5000)

- Senha padrão: `admin123`
- Para mudar: `set ADMIN_PASSWORD=sua-senha` (Windows) antes de rodar

## Por que o celular não abre o QR?

No modo local, o QR aponta para `http://127.0.0.1:5000/...`.  
`127.0.0.1` = **este computador**. O celular não enxerga o seu PC.

Para as placas funcionarem na rua, o site precisa estar **publicado na internet** com um domínio/URL pública.

## Deixar público (GitHub + Render)

Siga o guia: [DEPLOY.md](DEPLOY.md)

Depois de publicar, **baixe de novo** as plaquinhas PDF/PNG — os QR com localhost não funcionam fora do PC.
