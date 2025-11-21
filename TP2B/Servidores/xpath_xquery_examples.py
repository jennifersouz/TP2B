#!/usr/bin/env python3
"""
Exemplos práticos de XPath e XQuery para análise de dados de vendas
"""
from lxml import etree


class XMLQueryExamples:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.tree = etree.parse(xml_file)
        self.ns = {'ns': 'http://sales.example.com'}
    
    def example_1_basic_selection(self):
        """Exemplo 1: Seleção básica - Todos os pedidos"""
        print("\n" + "="*70)
        print("📌 Exemplo 1: Selecionar todos os Order IDs")
        print("="*70)
        
        xpath = "//ns:OrderID/text()"
        results = self.tree.xpath(xpath, namespaces=self.ns)
        
        print(f"XPath: {xpath}")
        print(f"Resultados encontrados: {len(results)}")
        print(f"Primeiros 5: {results[:5]}")
    
    def example_2_filtering(self):
        """Exemplo 2: Filtrar vendas acima de $1000"""
        print("\n" + "="*70)
        print("📌 Exemplo 2: Pedidos com vendas > $1000")
        print("="*70)
        
        xpath = "//ns:Record[ns:Sales > 1000]"
        results = self.tree.xpath(xpath, namespaces=self.ns)
        
        print(f"XPath: {xpath}")
        print(f"Pedidos encontrados: {len(results)}")
        
        # Mostrar detalhes dos primeiros 3
        for i, rec in enumerate(results[:3], 1):
            order_id = rec.find('.//ns:OrderID', self.ns).text
            sales = rec.find('.//ns:Sales', self.ns).text
            product = rec.find('.//ns:ProductName', self.ns).text
            print(f"\n  {i}. Order: {order_id}")
            print(f"     Produto: {product}")
            print(f"     Vendas: ${sales}")
    
    def example_3_aggregation(self):
        """Exemplo 3: Calcular total de vendas por região"""
        print("\n" + "="*70)
        print("📌 Exemplo 3: Total de vendas por região")
        print("="*70)
        
        regions = ['South', 'West', 'East', 'Central']
        
        for region in regions:
            xpath = f"sum(//ns:Record[ns:Region='{region}']/ns:Sales)"
            total = self.tree.xpath(xpath, namespaces=self.ns)
            print(f"  {region:10s}: ${total:,.2f}")
    
    def example_4_count(self):
        """Exemplo 4: Contar pedidos por categoria"""
        print("\n" + "="*70)
        print("📌 Exemplo 4: Contagem de pedidos por categoria")
        print("="*70)
        
        categories = ['Furniture', 'Office Supplies', 'Technology']
        
        for category in categories:
            xpath = f"count(//ns:Record[ns:Category='{category}'])"
            count = int(self.tree.xpath(xpath, namespaces=self.ns))
            print(f"  {category:20s}: {count:5d} pedidos")
    
    def example_5_complex_filter(self):
        """Exemplo 5: Consulta complexa com múltiplas condições"""
        print("\n" + "="*70)
        print("📌 Exemplo 5: Pedidos com lucro negativo em 2016")
        print("="*70)
        
        xpath = """//ns:Record[
            ns:Profit < 0 and 
            starts-with(ns:OrderDate, '2016')
        ]"""
        results = self.tree.xpath(xpath, namespaces=self.ns)
        
        print(f"Pedidos com prejuízo em 2016: {len(results)}")
        
        # Calcular prejuízo total
        xpath_sum = """sum(//ns:Record[
            ns:Profit < 0 and 
            starts-with(ns:OrderDate, '2016')
        ]/ns:Profit)"""
        total_loss = self.tree.xpath(xpath_sum, namespaces=self.ns)
        
        print(f"Prejuízo total: ${total_loss:,.2f}")
    
    def example_6_customer_analysis(self):
        """Exemplo 6: Análise de clientes"""
        print("\n" + "="*70)
        print("📌 Exemplo 6: Clientes únicos e seus gastos")
        print("="*70)
        
        # Obter todos os customer IDs únicos
        xpath = "//ns:CustomerID/text()"
        all_customers = self.tree.xpath(xpath, namespaces=self.ns)
        unique_customers = set(all_customers)
        
        print(f"Total de clientes únicos: {len(unique_customers)}")
        
        # Analisar top 5 clientes
        customer_totals = {}
        for customer in unique_customers:
            xpath = f"sum(//ns:Record[ns:CustomerID='{customer}']/ns:Sales)"
            total = self.tree.xpath(xpath, namespaces=self.ns)
            customer_totals[customer] = total
        
        # Ordenar e mostrar top 5
        top_customers = sorted(customer_totals.items(), 
                              key=lambda x: x[1], 
                              reverse=True)[:5]
        
        print("\nTop 5 clientes:")
        for i, (customer, total) in enumerate(top_customers, 1):
            # Obter nome do cliente
            xpath = f"//ns:Record[ns:CustomerID='{customer}']/ns:CustomerName/text()"
            name = self.tree.xpath(xpath, namespaces=self.ns)[0]
            print(f"  {i}. {name} ({customer}): ${total:,.2f}")
    
    def example_7_date_range(self):
        """Exemplo 7: Consultas por intervalo de datas"""
        print("\n" + "="*70)
        print("📌 Exemplo 7: Pedidos em novembro de 2016")
        print("="*70)
        
        xpath = """//ns:Record[
            starts-with(ns:OrderDate, '2016-11')
        ]"""
        results = self.tree.xpath(xpath, namespaces=self.ns)
        
        print(f"Pedidos em 2016-11: {len(results)}")
        
        # Calcular total
        xpath_sum = """sum(//ns:Record[
            starts-with(ns:OrderDate, '2016-11')
        ]/ns:Sales)"""
        total = self.tree.xpath(xpath_sum, namespaces=self.ns)
        
        print(f"Total de vendas: ${total:,.2f}")
    
    def example_8_product_analysis(self):
        """Exemplo 8: Análise de produtos"""
        print("\n" + "="*70)
        print("📌 Exemplo 8: Produtos mais vendidos (por quantidade)")
        print("="*70)
        
        # Agregar quantidades por produto
        xpath = "//ns:ProductName/text()"
        all_products = self.tree.xpath(xpath, namespaces=self.ns)
        unique_products = set(all_products)
        
        product_quantities = {}
        for product in unique_products:
            # Escapar aspas no nome do produto
            safe_product = product.replace("'", "&apos;")
            xpath = f"sum(//ns:Record[ns:ProductName='{safe_product}']/ns:Quantity)"
            try:
                total_qty = self.tree.xpath(xpath, namespaces=self.ns)
                product_quantities[product] = total_qty
            except:
                continue
        
        # Top 10
        top_products = sorted(product_quantities.items(), 
                             key=lambda x: x[1], 
                             reverse=True)[:10]
        
        print("\nTop 10 produtos mais vendidos:")
        for i, (product, qty) in enumerate(top_products, 1):
            print(f"  {i:2d}. {product[:50]:50s} | Qtd: {int(qty):4d}")
    
    def example_9_returned_items(self):
        """Exemplo 9: Análise de itens devolvidos"""
        print("\n" + "="*70)
        print("📌 Exemplo 9: Análise de devoluções")
        print("="*70)
        
        # Contar devoluções (assumindo que "Not" significa não devolvido)
        xpath_returned = "count(//ns:Record[ns:Returned != 'Not'])"
        xpath_not_returned = "count(//ns:Record[ns:Returned = 'Not'])"
        
        returned = int(self.tree.xpath(xpath_returned, namespaces=self.ns))
        not_returned = int(self.tree.xpath(xpath_not_returned, namespaces=self.ns))
        
        print(f"  Devolvidos: {returned}")
        print(f"  Não devolvidos: {not_returned}")
        
        if returned + not_returned > 0:
            rate = (returned / (returned + not_returned)) * 100
            print(f"  Taxa de devolução: {rate:.2f}%")
    
    def example_10_discount_analysis(self):
        """Exemplo 10: Análise de descontos"""
        print("\n" + "="*70)
        print("📌 Exemplo 10: Impacto dos descontos")
        print("="*70)
        
        # Pedidos com desconto
        xpath_with_discount = "count(//ns:Record[ns:Discount > 0])"
        xpath_no_discount = "count(//ns:Record[ns:Discount = 0])"
        
        with_discount = int(self.tree.xpath(xpath_with_discount, namespaces=self.ns))
        no_discount = int(self.tree.xpath(xpath_no_discount, namespaces=self.ns))
        
        print(f"  Com desconto: {with_discount}")
        print(f"  Sem desconto: {no_discount}")
        
        # Desconto médio
        xpath_avg = """sum(//ns:Record/ns:Discount) div 
                      count(//ns:Record[ns:Discount > 0])"""
        avg_discount = self.tree.xpath(xpath_avg, namespaces=self.ns)
        
        print(f"  Desconto médio: {avg_discount*100:.1f}%")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python xpath_xquery_examples.py <arquivo.xml>")
        sys.exit(1)
    
    xml_file = sys.argv[1]
    
    print("\n" + "="*70)
    print("🔍 EXEMPLOS DE CONSULTAS XPATH PARA ANÁLISE DE VENDAS")
    print("="*70)
    
    examples = XMLQueryExamples(xml_file)
    
    # Executar todos os exemplos
    examples.example_1_basic_selection()
    examples.example_2_filtering()
    examples.example_3_aggregation()
    examples.example_4_count()
    examples.example_5_complex_filter()
    examples.example_6_customer_analysis()
    examples.example_7_date_range()
    examples.example_8_product_analysis()
    examples.example_9_returned_items()
    examples.example_10_discount_analysis()
    
    print("\n" + "="*70)
    print("✅ Exemplos concluídos!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()