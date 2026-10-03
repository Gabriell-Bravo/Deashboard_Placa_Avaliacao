# Persistência dos dados no Render

## Por que os cadastros sumiram?

No Render, o disco padrão do app é **temporário**.
Cada novo deploy (ou reinício) pode apagar o banco SQLite.

Isso **não** é bug do sistema — é o comportamento padrão da hospedagem sem disco persistente.

## Como não perder mais (obrigatório)

No painel do Render, no seu Web Service:

1. Abra o serviço → **Disks** → **Add disk**
2. Configure:
   - **Name:** `qr-data`
   - **Mount Path:** `/var/data`
   - **Size:** `1 GB`
3. Em **Environment** adicione/altere:
   - `DATA_DIR` = `/var/data`
4. Salve e faça um **Manual Deploy** (Clear build cache não é necessário)

Depois disso, os cadastros, vendas e leituras ficam no disco persistente e **não somem** nos deploys.

## Backup opcional

No dashboard do sistema existe **Exportar backup**.
Baixe de vez em quando um JSON com todas as placas.
Se algo der errado, use **Importar backup**.
