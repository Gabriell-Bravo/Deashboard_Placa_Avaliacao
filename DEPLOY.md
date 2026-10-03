# Deploy (Render) + banco Neon

## Persistência dos dados (recomendado: Neon grátis)

No plano Free do Render **não tem Disk**.  
Para os cadastros não sumirem, use o Neon:

👉 Guia completo: [NEON.md](NEON.md)

Resumo:
1. Crie projeto em https://neon.tech  
2. Copie a `DATABASE_URL`  
3. No Render → Environment → adicione `DATABASE_URL`  
4. Deploy de novo  

## Deploy do código

```powershell
git push origin main
```

O Render atualiza sozinho.

## Backup

Mesmo com Neon, use **Exportar backup** de vez em quando.
