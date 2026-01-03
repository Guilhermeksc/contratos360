# Guia de Atualização para Angular 21

## Passos para Atualização

### 1. Backup do Projeto
Certifique-se de fazer commit das alterações atuais antes de prosseguir.

### 2. Remover node_modules e package-lock.json
```bash
rm -rf node_modules package-lock.json
```

### 3. Atualizar o Angular CLI globalmente (opcional)
```bash
npm install -g @angular/cli@21
```

### 4. Instalar as novas dependências
```bash
npm install
```

### 5. Executar migrações automáticas (se disponíveis)
```bash
ng update @angular/core@21 @angular/cli@21
```

### 6. Verificar e corrigir breaking changes
Após a instalação, verifique se há erros de compilação e ajuste conforme necessário.

### 7. Testar a aplicação
```bash
npm start
```

## Breaking Changes Conhecidos do Angular 21

- Verifique a documentação oficial do Angular 21 para breaking changes específicos
- Alguns pacotes podem precisar de atualização manual
- TypeScript pode precisar ser atualizado para uma versão compatível

## Notas Importantes

- O `angular.json` já está configurado corretamente para Angular 21
- O `package.json` foi atualizado com as versões do Angular 21
- Execute `npm install` para atualizar o `package-lock.json` automaticamente

