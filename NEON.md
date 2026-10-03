# Como configurar o Neon (banco grátis) com o Render

Assim os cadastros **não somem** nos deploys, sem pagar Disk no Render.

## 1) Criar conta no Neon

1. Acesse: https://neon.tech  
2. Clique em **Sign up** (pode entrar com Google/GitHub)  
3. Crie um projeto (nome livre, ex: `qr-plaquinhas`)  
4. Região: qualquer uma (ex: US East)

## 2) Copiar a connection string

1. No painel do Neon, abra o projeto  
2. Vá em **Dashboard** / **Connection details**  
3. Copie a URL que começa com:

`postgresql://...`

Exemplo (não use esta, use a sua):

`postgresql://user:senha@ep-xxxx.us-east-1.aws.neon.tech/neondb?sslmode=require`

## 3) Colocar no Render

1. Abra seu serviço no Render: https://dashboard.render.com  
2. Vá em **Environment**  
3. Clique em **Add Environment Variable**  
4. Configure:
   - **Key:** `DATABASE_URL`  
   - **Value:** cole a URL do Neon  
5. Salve (**Save Changes**)  
6. Faça **Manual Deploy** → **Deploy latest commit**

## 4) Subir o código atualizado

No seu PC, na pasta do projeto:

```powershell
git add -A
git commit -m "Adiciona suporte ao Neon (Postgres)"
git push origin main
```

Espere o deploy do Render terminar (fica verde).

## 5) Restaurar suas placas (se sumiram)

1. Entre no site  
2. Se tiver um backup JSON: **Importar backup**  
3. Se não tiver: cadastre de novo (agora já fica salvo no Neon)

## Pronto

- Local (seu PC): continua usando SQLite  
- Render: usa Neon automaticamente quando `DATABASE_URL` existir  

Os QR impressos continuam iguais (mesmo `PLACA-XXXX`), desde que o domínio do site seja o mesmo.
