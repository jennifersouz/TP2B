# grpc_server.py
#!/usr/bin/env python3
"""
Servidor gRPC para consultas de vendas em XML
"""
import grpc
from concurrent import futures
from lxml import etree
import sales_pb2
import sales_pb2_grpc


class SalesService(sales_pb2_grpc.SalesServiceServicer):
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
    
    def GetRecordsByRegion(self, request, context):
        """Buscar registros por região"""
        print(f"🔍 gRPC: Buscando região '{request.region}'")
        
        try:
            xpath = f"//ns:Record[ns:Region='{request.region}']"
            records = self.tree.xpath(xpath, namespaces=self.namespace)
            
            response_records = []
            for rec in records:
                response_records.append(self._xml_to_proto(rec))
            
            print(f"✅ Encontrados {len(response_records)} registros")
            return sales_pb2.RecordsResponse(
                records=response_records,
                total_count=len(response_records)
            )
        except Exception as e:
            context.set_details(f"Erro: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return sales_pb2.RecordsResponse()
    
    def GetRecordsByCategory(self, request, context):
        """Buscar registros por categoria"""
        print(f"🔍 gRPC: Buscando categoria '{request.category}'")
        
        try:
            xpath = f"//ns:Record[ns:Category='{request.category}']"
            records = self.tree.xpath(xpath, namespaces=self.namespace)
            
            response_records = []
            for rec in records:
                response_records.append(self._xml_to_proto(rec))
            
            print(f"✅ Encontrados {len(response_records)} registros")
            return sales_pb2.RecordsResponse(
                records=response_records,
                total_count=len(response_records)
            )
        except Exception as e:
            context.set_details(f"Erro: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return sales_pb2.RecordsResponse()
    
    def GetRecordsByCustomer(self, request, context):
        """Buscar registros por cliente"""
        print(f"🔍 gRPC: Buscando cliente '{request.customer_id}'")
        
        try:
            xpath = f"//ns:Record[ns:CustomerID='{request.customer_id}']"
            records = self.tree.xpath(xpath, namespaces=self.namespace)
            
            response_records = []
            for rec in records:
                response_records.append(self._xml_to_proto(rec))
            
            print(f"✅ Encontrados {len(response_records)} registros")
            return sales_pb2.RecordsResponse(
                records=response_records,
                total_count=len(response_records)
            )
        except Exception as e:
            context.set_details(f"Erro: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return sales_pb2.RecordsResponse()
    
    def GetSalesStats(self, request, context):
        """Obter estatísticas de vendas"""
        print(f"🔍 gRPC: Estatísticas por '{request.field}'")
        
        try:
            # Agrupar por campo solicitado
            field = request.field.lower()
            stats = {}
            
            records = self.tree.xpath("//ns:Record", namespaces=self.namespace)
            
            for rec in records:
                key = self._get_text(rec, field.capitalize())
                sales = float(self._get_text(rec, 'Sales') or 0)
                profit = float(self._get_text(rec, 'Profit') or 0)
                
                if key not in stats:
                    stats[key] = {'sales': 0, 'profit': 0, 'count': 0}
                
                stats[key]['sales'] += sales
                stats[key]['profit'] += profit
                stats[key]['count'] += 1
            
            # Construir resposta
            response = sales_pb2.StatsResponse()
            for key, values in stats.items():
                response.total_sales[key] = values['sales']
                response.total_profit[key] = values['profit']
                response.record_count[key] = values['count']
            
            print(f"✅ Estatísticas calculadas para {len(stats)} grupos")
            return response
            
        except Exception as e:
            context.set_details(f"Erro: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return sales_pb2.StatsResponse()
    
    def ExecuteXPath(self, request, context):
        """Consulta XPath personalizada"""
        print(f"🔍 gRPC: XPath '{request.xpath_query}'")
        
        try:
            results = self.tree.xpath(request.xpath_query, namespaces=self.namespace)
            
            str_results = []
            for res in results:
                if isinstance(res, etree._Element):
                    str_results.append(etree.tostring(res, encoding='unicode', pretty_print=True))
                else:
                    str_results.append(str(res))
            
            print(f"✅ XPath retornou {len(str_results)} resultados")
            return sales_pb2.XPathResponse(
                results=str_results,
                result_count=len(str_results)
            )
        except Exception as e:
            context.set_details(f"Erro XPath: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return sales_pb2.XPathResponse()
    
    def _xml_to_proto(self, xml_record):
        """Converte elemento XML para mensagem protobuf"""
        return sales_pb2.SalesRecord(
            row_id=int(self._get_text(xml_record, 'RowID') or 0),
            order_id=self._get_text(xml_record, 'OrderID'),
            order_date=self._get_text(xml_record, 'OrderDate'),
            ship_date=self._get_text(xml_record, 'ShipDate'),
            ship_mode=self._get_text(xml_record, 'ShipMode'),
            customer_id=self._get_text(xml_record, 'CustomerID'),
            customer_name=self._get_text(xml_record, 'CustomerName'),
            segment=self._get_text(xml_record, 'Segment'),
            country=self._get_text(xml_record, 'Country'),
            city=self._get_text(xml_record, 'City'),
            state=self._get_text(xml_record, 'State'),
            postal_code=self._get_text(xml_record, 'PostalCode'),
            region=self._get_text(xml_record, 'Region'),
            retail_sales_people=self._get_text(xml_record, 'RetailSalesPeople'),
            product_id=self._get_text(xml_record, 'ProductID'),
            category=self._get_text(xml_record, 'Category'),
            sub_category=self._get_text(xml_record, 'SubCategory'),
            product_name=self._get_text(xml_record, 'ProductName'),
            returned=self._get_text(xml_record, 'Returned'),
            sales=float(self._get_text(xml_record, 'Sales') or 0),
            quantity=int(self._get_text(xml_record, 'Quantity') or 0),
            discount=float(self._get_text(xml_record, 'Discount') or 0),
            profit=float(self._get_text(xml_record, 'Profit') or 0)
        )
    
    def _get_text(self, element, tag):
        """Extrai texto de um elemento XML"""
        elem = element.find(f'.//ns:{tag}', self.namespace)
        return elem.text if elem is not None else ""


def serve(xml_file='output.xml', host='localhost', port=50051):
    """Inicia o servidor gRPC"""
    print(f"🚀 Iniciando servidor gRPC em {host}:{port}")
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sales_pb2_grpc.add_SalesServiceServicer_to_server(
        SalesService(xml_file), server
    )
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    
    print(f"✅ Servidor gRPC pronto!")
    print(f"   Endpoint: {host}:{port}")
    print(f"   Métodos disponíveis:")
    print(f"   - GetRecordsByRegion")
    print(f"   - GetRecordsByCategory") 
    print(f"   - GetRecordsByCustomer")
    print(f"   - GetSalesStats")
    print(f"   - ExecuteXPath")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n🛑 Encerrando servidor gRPC...")
        server.stop(0)


if __name__ == '__main__':
    import sys
    xml_file = sys.argv[1] if len(sys.argv) > 1 else 'output.xml'
    host = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 50051
    
    serve(xml_file, host, port)