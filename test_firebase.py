#!/usr/bin/env python3
"""
Script de teste para verificar a integração Firebase
Execute localmente para testar antes do deploy
"""

import sys
import os
from datetime import datetime

# Adicionar path para config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_firestore_connection():
    """Testa conexão com Firestore"""
    try:
        from config.firebase_config import init_firebase
        
        print("🔥 Testando conexão Firestore...")
        db = init_firebase()
        
        if db:
            # Teste de escrita
            test_data = {
                'timestamp': datetime.now().isoformat(),
                'app': 'RST',
                'status': 'teste_script',
                'versao': '2.1.0'
            }
            
            doc_ref = db.collection('testes').add(test_data)
            print(f"✅ Firestore OK - Documento criado: {doc_ref[1].id}")
            
            # Teste de leitura
            docs = list(db.collection('testes').limit(1).stream())
            print(f"✅ Leitura OK - {len(docs)} documentos encontrados")
            
            return True
        else:
            print("❌ Falha na inicialização do Firestore")
            return False
            
    except Exception as e:
        print(f"❌ Erro Firestore: {e}")
        return False

def test_storage_config():
    """Testa configuração do Storage"""
    try:
        from firebase_admin import storage
        
        print("📁 Testando configuração Storage...")
        
        # Tentar obter bucket
        bucket = storage.bucket("apprst-baa01.firebasestorage.app")
        print(f"✅ Bucket configurado: {bucket.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro Storage: {e}")
        return False

def test_collections_structure():
    """Testa estrutura das coleções"""
    try:
        from config.firebase_config import init_firebase
        
        print("📊 Testando estrutura de coleções...")
        db = init_firebase()
        
        # Testar coleção custos_contabeis
        custos_ref = db.collection('custos_contabeis')
        custos = list(custos_ref.limit(1).stream())
        print(f"✅ Coleção custos_contabeis: {len(custos)} documentos")
        
        # Criar exemplo de custo se não existir
        if len(custos) == 0:
            exemplo_custo = {
                'data': '2024-08-20',
                'tipo_custo': 'Custos Variáveis',
                'categoria': 'fertilizantes',
                'categoria_nome': 'Fertilizantes',
                'valor': 100.0,
                'fornecedor': 'Fornecedor Teste',
                'numero_nf': 'TESTE123',
                'tem_nota_fiscal': False,
                'observacoes': 'Teste de estrutura',
                'timestamp': datetime.now().isoformat(),
                'app_version': 'RST_v2.1'
            }
            
            doc_ref = custos_ref.add(exemplo_custo)
            print(f"✅ Exemplo de custo criado: {doc_ref[1].id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro estrutura: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🧪 INICIANDO TESTES FIREBASE RST")
    print("=" * 50)
    
    tests = [
        ("Firestore Connection", test_firestore_connection),
        ("Storage Configuration", test_storage_config),
        ("Collections Structure", test_collections_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 RESULTADOS DOS TESTES:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 Firebase está pronto para produção!")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM!")
        print("🔧 Verifique as configurações no Firebase Console")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)