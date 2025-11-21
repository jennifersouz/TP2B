#!/usr/bin/env python3
"""
Conversor CSV para XML com validação por Schema XSD - VERSÃO CORRIGIDA
"""
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
from lxml import etree
from datetime import datetime
import sys
import os


class CSVtoXMLConverter:
    def __init__(self, csv_file, xml_file, xsd_file=None):
        self.csv_file = csv_file
        self.xml_file = xml_file
        self.xsd_file = xsd_file
        self.namespace = "http://sales.example.com"
        
    def parse_date(self, date_str):
        """Converte string para formato ISO de data"""
        try:
            # Tenta vários formatos de data
            formats = [
                "%Y-%m-%d",
                "%d/%m/%Y", 
                "%m/%d/%Y",
                "%d-%m-%Y",
                "%m-%d-%Y"
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%Y-%m-%d")
                except:
                    continue
            
            return date_str  # Retorna original se não conseguir converter
        except:
            return date_str
    
    def clean_value(self, value):
        """Limpa e formata valores"""
        if value is None:
            return ""
        return str(value).strip()
    
    def convert(self):
        """Converte CSV para XML - VERSÃO CORRIGIDA"""
        print(f"🔄 Convertendo {self.csv_file} para XML...")
        
        # Verificar se o arquivo CSV existe
        if not os.path.exists(self.csv_file):
            print(f"❌ Arquivo CSV não encontrado: {self.csv_file}")
            return 0
        
        # Criar elemento raiz com namespace
        ET.register_namespace('', self.namespace)
        root = ET.Element(f"{{{self.namespace}}}SalesRecords")
        
        # Ler CSV e criar elementos XML
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            
            # Mostrar as colunas encontradas (para debug)
            print(f"📋 Colunas detectadas: {reader.fieldnames}")
            
            for row in reader:
                # VERIFICAÇÃO: Pular linhas vazias ou com dados insuficientes
                if not row or len(row) < 5:  # Se menos de 5 colunas com dados
                    continue
                    
                record = ET.SubElement(root, f"{{{self.namespace}}}Record")
                
                # Mapeamento de campos
                fields = {
                    'RowID': 'Row ID',
                    'OrderID': 'Order ID',
                    'OrderDate': 'Order Date',
                    'ShipDate': 'Ship Date',
                    'ShipMode': 'Ship Mode',
                    'CustomerID': 'Customer ID',
                    'CustomerName': 'Customer Name',
                    'Segment': 'Segment',
                    'Country': 'Country',
                    'City': 'City',
                    'State': 'State',
                    'PostalCode': 'Postal Code',
                    'Region': 'Region',
                    'RetailSalesPeople': 'Retail Sales People',
                    'ProductID': 'Product ID',
                    'Category': 'Category',
                    'SubCategory': 'Sub-Category',
                    'ProductName': 'Product Name',
                    'Returned': 'Returned',
                    'Sales': 'Sales',
                    'Quantity': 'Quantity',
                    'Discount': 'Discount',
                    'Profit': 'Profit'
                }
                
                for xml_field, csv_field in fields.items():
                    elem = ET.SubElement(record, f"{{{self.namespace}}}{xml_field}")
                    value = self.clean_value(row.get(csv_field, ''))
                    
                    # Formatar datas
                    if 'Date' in xml_field:
                        value = self.parse_date(value)
                    
                    elem.text = value
                
                count += 1
                if count % 1000 == 0:
                    print(f"  Processados {count} registros...")
        
        # Criar árvore XML
        tree = ET.ElementTree(root)
        
        # Salvar com indentação
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")
        
        with open(self.xml_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        print(f"✅ Convertidos {count} registros para {self.xml_file}")
        
        # Validar se XSD foi fornecido
        if self.xsd_file and os.path.exists(self.xsd_file):
            self.validate()
        elif self.xsd_file:
            print(f"⚠️  Arquivo XSD não encontrado: {self.xsd_file}")
        
        return count
    
    def validate(self):
        """Valida XML contra o schema XSD"""
        print(f"\n🔍 Validando XML contra schema {self.xsd_file}...")
        
        try:
            # Verificar se o schema existe e não está vazio
            if not os.path.exists(self.xsd_file) or os.path.getsize(self.xsd_file) == 0:
                print("❌ Arquivo XSD não encontrado ou vazio")
                return
                
            # Carregar XSD
            with open(self.xsd_file, 'r', encoding='utf-8') as f:
                schema_root = etree.XML(f.read().encode('utf-8'))
            schema = etree.XMLSchema(schema_root)
            
            # Carregar XML
            with open(self.xml_file, 'r', encoding='utf-8') as f:
                xml_doc = etree.parse(f)
            
            # Validar
            if schema.validate(xml_doc):
                print("✅ XML válido conforme o schema!")
            else:
                print("❌ Erros de validação encontrados:")
                for error in schema.error_log:
                    print(f"  Linha {error.line}: {error.message}")
                    
        except Exception as e:
            print(f"❌ Erro durante validação: {e}")


def main():
    if len(sys.argv) < 3:
        print("Uso: python csv_to_xml_converter.py <arquivo.csv> <saida.xml> [schema.xsd]")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    xml_file = sys.argv[2]
    xsd_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    converter = CSVtoXMLConverter(csv_file, xml_file, xsd_file)
    converter.convert()


if __name__ == "__main__":
    main()