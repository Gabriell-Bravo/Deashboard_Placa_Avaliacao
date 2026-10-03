# Deploy no Render (grátis) via GitHub

O GitHub **não executa** Flask. Ele só guarda o código.
O fluxo que funciona:

1. Código no GitHub
2. Render puxa do GitHub e sobe o site na internet
3. QR codes passam a usar a URL pública (`https://....onrender.com`)

## Passo a passo

### 1. Subir o código no GitHub
Crie um repositório (pode ser privado) e envie esta pasta.

### 2. Criar app no Render
1. Acesse https://render.com e entre com GitHub
2. **New → Web Service**
3. Selecione este repositório
4. Render detecta o `render.yaml` / `Procfile`
5. Em Environment Variables, confira:
   - `ADMIN_PASSWORD` = sua senha do painel
   - `SECRET_KEY` = (Render pode gerar)
6. Clique em **Create Web Service**

### 3. Depois que subir
- Abra a URL `https://seu-app.onrender.com`
- Entre com a senha
- **Baixe de novo** as plaquinhas PDF/PNG (os QR antigos com localhost não valem)

## Observações
- No plano free o Render pode “dormir” após ~15 min sem acesso (primeira abertura fica lenta)
- O banco SQLite no free pode resetar em alguns redeploys; para uso sério, depois dá para colocar disco persistente
