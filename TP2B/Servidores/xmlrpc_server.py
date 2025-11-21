#!/usr/bin/env python3
"""
Servidor XML-RPC para consultas de vendas em XML
"""
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from lxml import etree
import logging


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class SalesXMLRPCService:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.namespace = {'ns': 'http://sales.example.com'}
        self.tree = None
        self.load_xml()
    
    def load_xml(self):
        """Carrega o arquivo XML"""
        print(f"📂 Carregando {self.xml_file}...")
        try:
            self.tree = etree.parse(self.xml_file)
            print("✅ XML carregado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar XML: {e}")
            raise
    
    def get_records_by_region(self, region):
        """Retorna registros filtrados por região"""
        print(f"🔍 XML-RPC: Buscando região '{region}'")
        
        xpath = f"//ns:Record[ns:Region='{region}']"
        records = self.tree.xpath(xpath, namespaces=self.namespace)
        
        result = []
        for rec in records:
            result.append({
                'order_id': self._get_text(rec, 'OrderID'),
                'customer_name': self._get_text(rec, 'CustomerName'),
                'city': self._get_text(rec, 'City'),
                'sales': float(self._get_text(rec, 'Sales') or 0),
                'profit': float(self._get_text(rec, 'Profit') or 0)
            })
        
        print(f"✅ Encontrados {len(result)} registros")
        return result
    
    def get_records_by_category(self, category):
        """Retorna registros filtrados por categoria"""
        print(f"🔍 XML-RPC: Buscando categoria '{category}'")
        
        xpath = f"//ns:Record[ns:Category='{category}']"
        records = self.tree.xpath(xpath, namespaces=self.namespace)
        
        result = []
        for rec in records:
            result.append({
                'product_name': self._get_text(rec, 'ProductName'),
                'sub_category': self._get_text(rec, 'SubCategory'),
                'quantity': int(self._get_text(rec, 'Quantity') or 0),
                'sales': float(self._get_text(rec, 'Sales') or 0)
            })
        
        print(f"✅ Encontrados {len(result)} registros")
        return result
    
    def get_customer_orders(self, customer_id):
        """Retorna pedidos de um cliente específico"""
        print(f"🔍 XML-RPC: Buscando cliente '{customer_id}'")
        
        xpath = f"//ns:Record[ns:CustomerID='{customer_id}']"
        records = self.tree.xpath(xpath, namespaces=self.namespace)
        
        result = []
        for rec in records:
            result.append({
                'order_id': self._get_text(rec, 'OrderID'),
                'order_date': self._get_text(rec, 'OrderDate'),
                'product_name': self._get_text(rec, 'ProductName'),
                'sales': float(self._get_text(rec, 'Sales') or 0),
                'profit': float(self._get_text(rec, 'Profit') or 0)
            })
        
        print(f"✅ Encontrados {len(result)} pedidos")
        return result
    
    def get_top_products(self, limit=10):
        """Retorna os produtos com maior venda"""
        print(f"🔍 XML-RPC: Buscando top {limit} produtos")
        
        # Agregar vendas por produto
        products = {}
        records = self.tree.xpath("//ns:Record", namespaces=self.namespace)
        
        for rec in records:
            product_name = self._get_text(rec, 'ProductName')
            sales = float(self._get_text(rec, 'Sales') or 0)
            
            if product_name in products:
                products[product_name] += sales
            else:
                products[product_name] = sales
        
        # Ordenar e retornar top N
        sorted_products = sorted(products.items(), key=lambda x: x[1], reverse=True)
        result = [{'product': p[0], 'total_sales': p[1]} for p in sorted_products[:limit]]
        
        print(f"✅ Retornados {len(result)} produtos")
        return result
    
    def get_sales_by_state(self):
        """Retorna vendas agregadas por estado"""
        print(f"🔍 XML-RPC: Calculando vendas por estado")
        
        states = {}
        records = self.tree.xpath("//ns:Record", namespaces=self.namespace)
        
        for rec in records:
            state = self._get_text(rec, 'State')
            sales = float(self._get_text(rec, 'Sales') or 0)
            profit = float(self._get_text(rec, 'Profit') or 0)
            
            if state not in states:
                states[state] = {'sales': 0, 'profit': 0, 'count': 0}
            
            states[state]['sales'] += sales
            states[state]['profit'] += profit
            states[state]['count'] += 1
        
        result = [{'state': k, **v} for k, v in states.items()]
        
        print(f"✅ Calculados dados para {len(result)} estados")
        return result
    
    def execute_xpath(self, xpath_query):
        """Executa uma consulta XPath personalizada"""
        print(f"🔍 XML-RPC: Executando XPath '{xpath_query}'")
        
        try:
            results = self.tree.xpath(xpath_query, namespaces=self.namespace)
            
            str_results = []
            for res in results:
                if isinstance(res, etree._Element):
                    str_results.append(etree.tostring(res, encoding='unicode'))
                else:
                    str_results.append(str(res))
            
            print(f"✅ XPath retornou {len(str_results)} resultados")
            return str_results
        except Exception as e:
            print(f"❌ Erro ao executar XPath: {e}")
            return {'error': str(e)}
    
    def _get_text(self, element, tag):
        """Extrai texto de um elemento XML"""
        elem = element.find(f'.//ns:{tag}', self.namespace)
        return elem.text if elem is not None else ""


def serve(xml_file='sales_data.xml', host='localhost', port=8000):
    """Inicia o servidor XML-RPC"""
    print(f"🚀 Iniciando servidor XML-RPC em {host}:{port}")
    
    server = SimpleXMLRPCServer(
        (host, port),
        requestHandler=RequestHandler,
        allow_none=True
    )
    
    server.register_introspection_functions()
    
    # Registrar serviço
    service = SalesXMLRPCService(xml_file)
    server.register_instance(service)
    
    print(f"✅ Servidor XML-RPC pronto!")
    print(f"   Endpoint: http://{host}:{port}/RPC2")
    print(f"   Métodos disponíveis:")
    print(f"   - get_records_by_region(region)")
    print(f"   - get_records_by_category(category)")
    print(f"   - get_customer_orders(customer_id)")
    print(f"   - get_top_products(limit)")
    print(f"   - get_sales_by_state()")
    print(f"   - execute_xpath(xpath_query)")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Encerrando servidor XML-RPC...")


if __name__ == '__main__':
    import sys
    xml_file = sys.argv[1] if len(sys.argv) > 1 else 'sales_data.xml'
    host = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
    
    serve(xml_file, host, port)