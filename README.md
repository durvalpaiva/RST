# 🚜 RST - Sistema de Gestão de Custos para Fazenda

Sistema completo de gestão financeira para propriedades rurais desenvolvido com Streamlit e Firebase.

## 📋 Funcionalidades

### 💰 Gestão de Custos
- **Classificação Contábil**: Custos Fixos, Variáveis e Investimentos
- **Categorias Específicas**: 31 categorias pré-definidas para o agronegócio
- **Upload de Notas Fiscais**: Anexar fotos direto da câmera mobile
- **Dados do Fornecedor**: Registro completo com número da NF
- **Cálculo de Depreciação**: Automático para investimentos

### 📊 Análise e Relatórios
- **Tabelas Filtráveis**: Por tipo, valor, data e categoria
- **Exportação CSV**: Download dos dados para análise externa
- **Gráficos Evolutivos**: Visualização temporal dos custos
- **Métricas em Tempo Real**: Totais por categoria e período

### 📱 Interface Mobile
- **Responsiva**: Otimizada para smartphones e tablets
- **Câmera Integrada**: Foto direta das notas fiscais
- **Toggle Forms**: Interface limpa com formulários ocultáveis

## 🛠️ Tecnologias Utilizadas

- **Frontend**: Streamlit 1.28+
- **Backend**: Firebase Admin SDK
- **Database**: Cloud Firestore (NoSQL)
- **Storage**: Firebase Storage
- **Linguagem**: Python 3.8+
- **Deploy**: Streamlit Cloud

## 📦 Instalação Local

### 1. Clonar o Repositório
```bash
git clone https://github.com/durvalpaiva/RST.git
cd RST
```

### 2. Criar Ambiente Virtual
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Firebase
1. Crie um projeto no [Firebase Console](https://console.firebase.google.com)
2. Ative Firestore Database e Storage
3. Baixe a chave de serviço (arquivo JSON)
4. Configure as variáveis de ambiente

### 5. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=seu_project_id
FIREBASE_PRIVATE_KEY_ID=sua_private_key_id
FIREBASE_PRIVATE_KEY=sua_private_key
FIREBASE_CLIENT_EMAIL=seu_client_email
FIREBASE_CLIENT_ID=seu_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
```

### 6. Executar Aplicação
```bash
streamlit run main.py
```

## 🚀 Deploy no Streamlit Cloud

### 1. Preparar Repositório
- Fork este repositório
- Configure os secrets no Streamlit Cloud

### 2. Configurar Secrets
No painel do Streamlit Cloud, adicione em **Settings → Secrets**:
```toml
[firebase]
type = "service_account"
project_id = "seu_project_id"
private_key_id = "sua_private_key_id"
private_key = "-----BEGIN PRIVATE KEY-----\nsua_chave_privada\n-----END PRIVATE KEY-----"
client_email = "seu_client_email"
client_id = "seu_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/seu_client_email"

[general]
storage_bucket = "seu_bucket.firebasestorage.app"
```

### 3. Deploy
- Conecte seu repositório GitHub
- Defina `main.py` como arquivo principal
- Clique em Deploy

## 📚 Estrutura do Projeto

```
RST/
├── config/
│   └── firebase_config.py      # Configuração Firebase
├── pages/
│   └── 01_💰_Custos.py        # Página principal de custos
├── main.py                     # Aplicação principal
├── requirements.txt            # Dependências Python
├── test_firebase.py           # Testes de conexão
├── FIREBASE_SETUP.md          # Guia de configuração
└── README.md                  # Este arquivo
```

## 💡 Categorias de Custos

### 🔒 Custos Fixos (8 categorias)
- Salários, Internet, Telefone, Manutenção, Sistema, Impostos, Consultoria, Marketing

### 📈 Custos Variáveis (13 categorias)
- Sementes, Fertilizantes, Defensivos, Nutrientes, Embalagens, Frete, Combustível, etc.

### 💎 Investimentos (10 categorias)
- Equipamentos, Tecnologia, Veículos, Irrigação, Construção, Infraestrutura, etc.

## 🧪 Testes

Execute os testes de conexão Firebase:
```bash
python test_firebase.py
```

## 📖 Guia de Uso

1. **Cadastro de Custos**: Use o formulário toggle para adicionar novos registros
2. **Upload de NF**: Tire foto diretamente ou selecione arquivo
3. **Visualização**: Use filtros para analisar dados específicos
4. **Exportação**: Baixe relatórios em CSV para análise externa
5. **Métricas**: Acompanhe totais e médias em tempo real

## 🔧 Configuração Firebase

Consulte o arquivo `FIREBASE_SETUP.md` para instruções detalhadas de:
- Configuração do Firestore
- Regras de segurança
- Configuração do Storage
- Estrutura das coleções

## 📱 Uso Mobile

O sistema é otimizado para uso mobile:
- Interface responsiva
- Câmera integrada para NF
- Formulários compactos
- Navegação touch-friendly

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Durval Paiva**
- GitHub: [@durvalpaiva](https://github.com/durvalpaiva)

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação no `FIREBASE_SETUP.md`
2. Execute `python test_firebase.py` para diagnosticar conexões
3. Abra uma issue no GitHub

---

**🚜 RST - Gestão Inteligente para o Agronegócio** 🌾