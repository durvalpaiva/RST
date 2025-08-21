# 🔥 Configuração Completa do Firebase - Projeto RST

## 📋 **PASSOS OBRIGATÓRIOS NO FIREBASE CONSOLE**

### 1. 🗄️ **Configurar Firestore Database**

#### **Ir para Firestore Database:**
```
Firebase Console → Seu Projeto (apprst-baa01) → Firestore Database
```

#### **Configurar Regras de Segurança:**
```javascript
// Rules for Cloud Firestore
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Permitir leitura e escrita para custos contábeis
    match /custos_contabeis/{document} {
      allow read, write: if true;
    }
    
    // Permitir leitura e escrita para testes
    match /testes/{document} {
      allow read, write: if true;
    }
    
    // Permitir leitura e escrita para outras coleções futuras
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

### 2. 📁 **Configurar Firebase Storage**

#### **Ir para Storage:**
```
Firebase Console → Seu Projeto (apprst-baa01) → Storage
```

#### **Clicar em "Começar"**
- Escolher "Começar no modo de teste"
- Selecionar localização: `southamerica-east1 (São Paulo)`

#### **Configurar Regras de Segurança do Storage:**
```javascript
// Rules for Cloud Storage
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Permitir upload de imagens de notas fiscais
    match /notas_fiscais/{allPaths=**} {
      allow read, write: if true;
    }
    
    // Permitir outros uploads futuros
    match /{allPaths=**} {
      allow read, write: if true;
    }
  }
}
```

### 3. 🔧 **Verificar Configurações do Projeto**

#### **Configurações → Geral:**
- Nome do projeto: `AppRST`
- ID do projeto: `apprst-baa01`
- Storage bucket: `apprst-baa01.firebasestorage.app`

#### **Configurações → Contas de Serviço:**
- Verificar se o arquivo JSON está correto
- Chave deve ter permissões de admin

## 📊 **ESTRUTURA DAS COLEÇÕES NO FIRESTORE**

### **Coleção: `custos_contabeis`**
```javascript
{
  "data": "2024-08-20",
  "tipo_custo": "Custos Variáveis",
  "categoria": "fertilizantes",
  "categoria_nome": "Fertilizantes",
  "valor": 150.00,
  "fornecedor": "Agropecuária Silva Ltda",
  "numero_nf": "123456",
  "imagem_nf_url": "https://firebasestorage.googleapis.com/v0/b/apprst-baa01.appspot.com/o/notas_fiscais%2F20240820_143022_abc123.jpg?alt=media",
  "tem_nota_fiscal": true,
  "observacoes": "Fertilizante para alface",
  "lote_producao": "ALFACE_001",
  "timestamp": "2024-08-20T14:30:22.123Z",
  "app_version": "RST_v2.1"
}
```

### **Coleção: `testes` (para validação)**
```javascript
{
  "timestamp": "2024-08-20T14:30:22.123Z",
  "app": "RST",
  "status": "teste_funcionando",
  "versao": "1.0.0"
}
```

## 📁 **ESTRUTURA DO FIREBASE STORAGE**

```
apprst-baa01.firebasestorage.app/
├── notas_fiscais/
│   ├── 20240820_143022_abc123.jpg
│   ├── 20240820_143055_def456.png
│   └── 20240820_143120_ghi789.pdf
├── documentos/
│   └── (arquivos futuros)
└── backup/
    └── (backups futuros)
```

## 🔐 **CONFIGURAÇÃO DE SECRETS NO STREAMLIT CLOUD**

### **Arquivo: `.streamlit/secrets.toml`**
```toml
[firebase]
type = "service_account"
project_id = "SEU_PROJECT_ID"
private_key_id = "SUA_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\nSUA_CHAVE_PRIVADA_AQUI\n-----END PRIVATE KEY-----\n"
client_email = "SEU_CLIENT_EMAIL@projeto.iam.gserviceaccount.com"
client_id = "SEU_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/SEU_CLIENT_EMAIL"

[general]
storage_bucket = "SEU_BUCKET.firebasestorage.app"
```

## ✅ **CHECKLIST DE VERIFICAÇÃO**

### **No Firebase Console:**
- [ ] Firestore Database criado
- [ ] Regras de segurança do Firestore configuradas
- [ ] Storage criado
- [ ] Regras de segurança do Storage configuradas
- [ ] Bucket name: `SEU_BUCKET.firebasestorage.app`

### **No Streamlit Cloud:**
- [ ] Secrets configurados
- [ ] Deploy funcionando
- [ ] Teste de conexão passando

### **Testes Funcionais:**
- [ ] Salvar custo sem foto
- [ ] Salvar custo com foto
- [ ] Visualizar dados nas tabelas
- [ ] Download de CSV funcionando

## 🚨 **COMANDOS PARA TESTAR LOCALMENTE**

### **Teste 1: Conexão Firestore**
```python
# No streamlit app, clicar em "Testar Conexão Firebase"
# Deve retornar: "Conexão com Firebase OK!"
```

### **Teste 2: Upload de Imagem**
```python
# Fazer upload de uma foto no formulário
# Verificar se URL é gerada
# Conferir no Storage se arquivo foi salvo
```

### **Teste 3: Dados Persistindo**
```python
# Adicionar vários custos
# Recarregar página
# Verificar se dados continuam lá
```

---

## 🔥 **PRÓXIMOS PASSOS:**

1. **Execute estas configurações** no Firebase Console
2. **Configure os secrets** no Streamlit Cloud  
3. **Faça o deploy** atualizado
4. **Teste todas as funcionalidades**
5. **Me informe** se algum passo deu erro

**Depois disso, os dados e imagens estarão 100% persistindo no Firebase!** 🚜