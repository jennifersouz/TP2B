#!/usr/bin/env python3
"""
Dashboard Interativo para Análise de Vendas - VERSÃO SIMPLES
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import grpc
import xmlrpc.client
import sales_pb2
import sales_pb2_grpc

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide"
)

# Título
st.title("Análise de Vendas")
st.markdown("---")

class DashboardData:
    def __init__(self):
        self.grpc_channel = grpc.insecure_channel('localhost:50051')
        self.grpc_stub = sales_pb2_grpc.SalesServiceStub(self.grpc_channel)
        self.xmlrpc_proxy = xmlrpc.client.ServerProxy('http://localhost:8000/RPC2')
    
    def get_sales_stats(self):
        """Obtém estatísticas via gRPC"""
        try:
            response = self.grpc_stub.GetSalesStats(sales_pb2.StatsRequest(field='region'))
            return response
        except:
            return None
    
    def get_top_products(self, limit=10):
        """Obtém produtos mais vendidos via XML-RPC"""
        try:
            return self.xmlrpc_proxy.get_top_products(limit)
        except:
            return []
    
    def get_sales_by_state(self):
        """Obtém vendas por estado via XML-RPC"""
        try:
            return self.xmlrpc_proxy.get_sales_by_state()
        except:
            return []

def main():
    data_client = DashboardData()
    
    # Métricas Principais (KPI Cards)
    st.subheader("Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        stats = data_client.get_sales_stats()
        
        with col1:
            total_sales = sum(stats.total_sales.values()) if stats else 0
            st.metric(
                label="Total de Vendas",
                value=f"${total_sales:,.2f}"
            )
        
        with col2:
            total_profit = sum(stats.total_profit.values()) if stats else 0
            st.metric(
                label="Lucro Total",
                value=f"${total_profit:,.2f}"
            )
        
        with col3:
            total_records = sum(stats.record_count.values()) if stats else 0
            st.metric(
                label="Total de Pedidos",
                value=f"{total_records:,}"
            )
        
        with col4:
            avg_sale = total_sales / total_records if total_records > 0 else 0
            st.metric(
                label="Ticket Médio",
                value=f"${avg_sale:.2f}"
            )
    
    except Exception as e:
        st.error(f"Erro ao carregar métricas: {e}")
    
    st.markdown("---")
    
    # Gráficos - Linha 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Vendas por Região")
        
        try:
            stats = data_client.get_sales_stats()
            if stats:
                regions = list(stats.total_sales.keys())
                sales = list(stats.total_sales.values())
                profits = list(stats.total_profit.values())
                
                # Gráfico de barras com vendas e lucro
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Vendas',
                    x=regions,
                    y=sales,
                    marker_color='lightblue'
                ))
                fig.add_trace(go.Bar(
                    name='Lucro',
                    x=regions,
                    y=profits,
                    marker_color='lightgreen'
                ))
                
                fig.update_layout(
                    title="Vendas e Lucro por Região",
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro no gráfico de regiões: {e}")
    
    with col2:
        st.subheader("Top 10 Produtos")
        
        try:
            top_products = data_client.get_top_products(10)
            if top_products:
                products = [p['product'][:30] + "..." if len(p['product']) > 30 else p['product'] for p in top_products]
                sales = [p['total_sales'] for p in top_products]
                
                fig = px.bar(
                    x=sales,
                    y=products,
                    orientation='h',
                    title="Produtos Mais Vendidos",
                    labels={'x': 'Vendas ($)', 'y': 'Produto'}
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro no gráfico de produtos: {e}")
    
    # Gráficos - Linha 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Estados com Maior Lucro")
        
        try:
            states_data = data_client.get_sales_by_state()
            if states_data:
                # Filtrar estados com lucro positivo
                estados_lucro = [s for s in states_data if s['profit'] > 0]
                estados_lucro = sorted(estados_lucro, key=lambda x: x['profit'], reverse=True)[:10]
                
                estados = [s['state'] for s in estados_lucro]
                lucros = [s['profit'] for s in estados_lucro]
                
                fig = px.bar(
                    x=estados,
                    y=lucros,
                    title="Top 10 Estados - Lucro",
                    labels={'x': 'Estado', 'y': 'Lucro ($)'},
                    color=lucros,
                    color_continuous_scale='greens'
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro no gráfico de lucros: {e}")
    
    with col2:
        st.subheader("Estados com Prejuízo")
        
        try:
            states_data = data_client.get_sales_by_state()
            if states_data:
                # Filtrar estados com prejuízo
                estados_prejuizo = [s for s in states_data if s['profit'] < 0]
                estados_prejuizo = sorted(estados_prejuizo, key=lambda x: x['profit'])[:10]  # Ordena do menor (mais negativo)
                
                if estados_prejuizo:
                    estados = [s['state'] for s in estados_prejuizo]
                    prejuizos = [s['profit'] for s in estados_prejuizo]
                    
                    fig = px.bar(
                        x=estados,
                        y=prejuizos,
                        title="Estados com Prejuízo",
                        labels={'x': 'Estado', 'y': 'Prejuízo ($)'},
                        color=prejuizos,
                        color_continuous_scale='reds'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.success("🎉 Nenhum estado com prejuízo!")
        except Exception as e:
            st.error(f"Erro no gráfico de prejuízos: {e}")
    
    # Tabela de Alertas
    st.subheader("Áreas de Atenção")
    
    try:
        states_data = data_client.get_sales_by_state()
        if states_data:
            problemas = [s for s in states_data if s['profit'] < 0]
            
            if problemas:
                df_problemas = pd.DataFrame(problemas)
                df_problemas['profit'] = df_problemas['profit'].apply(lambda x: f"${x:,.2f}")
                df_problemas['sales'] = df_problemas['sales'].apply(lambda x: f"${x:,.2f}")
                
                st.dataframe(
                    df_problemas[['state', 'sales', 'profit', 'count']],
                    column_config={
                        "state": "Estado",
                        "sales": "Vendas", 
                        "profit": "Prejuízo",
                        "count": "Pedidos"
                    },
                    use_container_width=True
                )
            else:
                st.success("Nenhuma área problemática identificada!")
    except Exception as e:
        st.error(f"Erro na tabela de alertas: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Desenvolvido com** Python • Streamlit • Docker • gRPC/XML-RPC"
    )

if __name__ == '__main__':
    main()