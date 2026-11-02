"""
Agregações mensais de clientes (fato_cliente_mes):
Calcula indicadores consolidados de faturamento, pedidos, itens e margem
diretamente a partir das transações de fato_venda e dim_produto, garantindo
reconciliação financeira exata.
"""

from database.connection import get_connection


def build_monthly_aggregations() -> int:
    """
    Executa a agregação mensal de vendas por cliente no PostgreSQL de forma idempotente.
    Retorna a quantidade de registros inseridos/atualizados na fato_cliente_mes.
    """
    query = """
    INSERT INTO fato_cliente_mes (
        id_cliente,
        mes_referencia,
        quantidade_pedidos,
        faturamento,
        ticket_medio,
        quantidade_itens,
        categorias_distintas,
        margem_total
    )
    SELECT 
        v.id_cliente,
        DATE_TRUNC('month', v.data_venda)::DATE AS mes_referencia,
        COUNT(DISTINCT v.data_venda) AS quantidade_pedidos,
        ROUND(SUM(v.valor_liquido), 2) AS faturamento,
        ROUND(SUM(v.valor_liquido) / NULLIF(COUNT(DISTINCT v.data_venda), 0), 2) AS ticket_medio,
        ROUND(SUM(v.quantidade), 3) AS quantidade_itens,
        COUNT(DISTINCT p.id_categoria) AS categorias_distintas,
        ROUND(SUM(v.margem_valor), 2) AS margem_total
    FROM fato_venda v
    JOIN dim_produto p ON v.id_produto = p.id_produto
    GROUP BY v.id_cliente, DATE_TRUNC('month', v.data_venda)::DATE
    ON CONFLICT (id_cliente, mes_referencia) DO UPDATE SET
        quantidade_pedidos = EXCLUDED.quantidade_pedidos,
        faturamento = EXCLUDED.faturamento,
        ticket_medio = EXCLUDED.ticket_medio,
        quantidade_itens = EXCLUDED.quantidade_itens,
        categorias_distintas = EXCLUDED.categorias_distintas,
        margem_total = EXCLUDED.margem_total;
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            affected = cur.rowcount
        conn.commit()
        return affected
    finally:
        conn.close()

