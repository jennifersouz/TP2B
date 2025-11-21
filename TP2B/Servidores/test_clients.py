#!/usr/bin/env python3
"""
Clientes de teste para gRPC e XML-RPC
"""
import grpc
import sales_pb2
import sales_pb2_grpc
import xmlrpc.client
from tabulate import tabulate


class GRPCClient:
    def __init__(self, host='localhost', port=50051):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = sales_pb2_grpc.SalesServiceStub(self.channel)
    
    def test_get_by_region(self, region='South'):
        print(f"\n{'='*60}")
        print(f"🧪 Teste gRPC: Registros da região '{region}'")
        print(f"{'='*60}")
        
        request = sales_pb2.RegionRequest(region=region)
        response = self.stub.GetRecordsByRegion(request)
        
        print(f"Total de registros: {response.total_count}")
        
        if response.records:
            data = []
            for rec in response.records[:5]:  # Mostrar apenas 5
                data.append([
                    rec.order_id,
                    rec.customer_name,
                    rec.city,
                    f"${rec.sales:.2f}",
                    f"${rec.profit:.2f}"
                ])
            
            print(tabulate(data, headers=['Order ID', 'Cliente', 'Cidade', 'Vendas', 'Lucro']))
            if response.total_count > 5:
                print(f"... e mais {response.total_count - 5} registros")
    
    def test_get_by_category(self, category='Furniture'):
        print(f"\n{'='*60}")
        print(f"🧪 Teste gRPC: Registros da categoria '{category}'")
        print(f"{'='*60}")
        
        request = sales_pb2.CategoryRequest(category=category)
        response = self.stub.GetRecordsByCategory(request)
        
        print(f"Total de registros: {response.total_count}")
        
        if response.records:
            data = []
            for rec in response.records[:5]:
                data.append([
                    rec.product_name[:40],
                    rec.sub_category,
                    rec.quantity,
                    f"${rec.sales:.2f}"
                ])
            
            print(tabulate(data, headers=['Produto', 'Subcategoria', 'Qtd', 'Vendas']))
            if response.total_count > 5:
                print(f"... e mais {response.total_count - 5} registros")
    
    def test_get_stats(self, field='region'):
        print(f"\n{'='*60}")
        print(f"🧪 Teste gRPC: Estatísticas por '{field}'")
        print(f"{'='*60}")
        
        request = sales_pb2.StatsRequest(field=field)
        response = self.stub.GetSalesStats(request)
        
        data = []
        for key in response.total_sales.keys():
            data.append([
                key,
                f"${response.total_sales[key]:,.2f}",
                f"${response.total_profit[key]:,.2f}",
                response.record_count[key]
            ])
        
        print(tabulate(data, headers=[field.capitalize(), 'Total Vendas', 'Total Lucro', 'Registros']))
    
    def test_xpath(self, xpath_query):
        print(f"\n{'='*60}")
        print(f"🧪 Teste gRPC: XPath Query")
        print(f"{'='*60}")
        print(f"Query: {xpath_query}")
        
        request = sales_pb2.XPathRequest(xpath_query=xpath_query)
        response = self.stub.ExecuteXPath(request)
        
        print(f"Resultados encontrados: {response.result_count}")
        for i, result in enumerate(response.results[:3], 1):
            print(f"\nResultado {i}:")
            print(result[:200] + "..." if len(result) > 200 else result)


class XMLRPCClient:
    def __init__(self, host='localhost', port=8000):
        self.proxy = xmlrpc.client.ServerProxy(f'http://{host}:{port}/RPC2')
    
    def test_get_by_region(self, region='West'):
        print(f"\n{'='*60}")
        print(f"🧪 Teste XML-RPC: Registros da região '{region}'")
        print(f"{'='*60}")
        
        records = self.proxy.get_records_by_region(region)
        print(f"Total de registros: {len(records)}")
        
        if records:
            data = []
            for rec in records[:5]:
                data.append([
                    rec['order_id'],
                    rec['customer_name'],
                    rec['city'],
                    f"${rec['sales']:.2f}",
                    f"${rec['profit']:.2f}"
                ])
            
            print(tabulate(data, headers=['Order ID', 'Cliente', 'Cidade', 'Vendas', 'Lucro']))
            if len(records) > 5:
                print(f"... e mais {len(records) - 5} registros")
    
    def test_top_products(self, limit=10):
        print(f"\n{'='*60}")
        print(f"🧪 Teste XML-RPC: Top {limit} Produtos")
        print(f"{'='*60}")
        
        products = self.proxy.get_top_products(limit)
        
        data = []
        for i, prod in enumerate(products, 1):
            data.append([
                i,
                prod['product'][:50],
                f"${prod['total_sales']:,.2f}"
            ])
        
        print(tabulate(data, headers=['Rank', 'Produto', 'Total Vendas']))
    
    def test_sales_by_state(self):
        print(f"\n{'='*60}")
        print(f"🧪 Teste XML-RPC: Vendas por Estado")
        print(f"{'='*60}")
        
        states = self.proxy.get_sales_by_state()
        
        # Ordenar por vendas
        states_sorted = sorted(states, key=lambda x: x['sales'], reverse=True)
        
        data = []
        for state in states_sorted[:10]:
            data.append([
                state['state'],
                f"${state['sales']:,.2f}",
                f"${state['profit']:,.2f}",
                state['count']
            ])
        
        print(tabulate(data, headers=['Estado', 'Vendas', 'Lucro', 'Pedidos']))
        print(f"\nMostrando top 10 de {len(states)} estados")


def main():
    print("\n" + "="*60)
    print("🚀 TESTE DE SERVIÇOS RPC - SISTEMA DE VENDAS")
    print("="*60)
    
    # Testar gRPC
    print("\n\n📡 TESTANDO SERVIDOR gRPC")
    print("="*60)
    
    try:
        grpc_client = GRPCClient()
        grpc_client.test_get_by_region('South')
        grpc_client.test_get_by_category('Furniture')
        grpc_client.test_get_stats('region')
        grpc_client.test_xpath("//ns:Record[ns:Sales > 1000]/ns:ProductName/text()")
    except Exception as e:
        print(f"❌ Erro ao testar gRPC: {e}")
    
    # Testar XML-RPC
    print("\n\n📡 TESTANDO SERVIDOR XML-RPC")
    print("="*60)
    
    try:
        xmlrpc_client = XMLRPCClient()
        xmlrpc_client.test_get_by_region('West')
        xmlrpc_client.test_top_products(10)
        xmlrpc_client.test_sales_by_state()
    except Exception as e:
        print(f"❌ Erro ao testar XML-RPC: {e}")
    
    print("\n\n✅ Testes concluídos!")


if __name__ == '__main__':
    main()