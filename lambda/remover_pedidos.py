import psycopg2
import os
from datetime import datetime

def lambda_handler(event, context):
    pedidosParaRemover = ()

    # Configurações dos bancos de dados - Pedidos
    host = os.environ['PEDIDOS_DB_HOST']
    database = os.environ['PEDIDOS_DB_NAME']
    user = os.environ['PEDIDOS_DB_USER']
    password = os.environ['PEDIDOS_DB_PASSWORD']

    # Conectar ao banco de dados - Pedidos
    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        print("Conexão bem-sucedida!")
        cur = conn.cursor()

        # Buscar Ids de pedidos expirados
        query_pedidosexpirados = """
            SELECT p."Id"
                FROM public."Pedido" p
                WHERE p."PagamentoConfirmado" = FALSE
                AND p."HorarioRecebimento" < NOW() - INTERVAL '15 minutes';
        """

        cur.execute(query_pedidosexpirados)

        pedidosexpirados_aux = cur.fetchall()

        pedidosParaRemover = tuple(row[0] for row in pedidosexpirados_aux)
        
        print('Ids salvos para remocao de acompanhamento:')
        print(pedidosParaRemover)

        # Excluir registros relacionados na tabela ItemPedido
        query_itempedido = """
            DELETE FROM public."ItemPedido"
            WHERE "PedidoAggregateId" IN (
                SELECT p."Id"
                FROM public."Pedido" p
                WHERE p."PagamentoConfirmado" = FALSE
                AND p."HorarioRecebimento" < NOW() - INTERVAL '15 minutes'
            );
        """

        # Executar a query para remover da tabela ItemPedido
        cur.execute(query_itempedido)

        # Excluir os registros da tabela Pedido
        query_pedido = """
        DELETE FROM public."Pedido" p
        WHERE p."PagamentoConfirmado" = FALSE
        AND p."HorarioRecebimento" < NOW() - INTERVAL '15 minutes'
        """

        # Executar a query para remover da tabela Pedido
        cur.execute(query_pedido)

        # Aplicar as mudanças no banco de dados
        conn.commit()

        # Fechar cursor e conexão
        cur.close()
        print(f"Pedidos com status 'recebido' (1) e HorarioRecebimento superior a 15 minutos removidos em {datetime.now()}.")
    except Exception as e:
        print(f"Erro ao conectar em Acompanhamentos: {e}")
        return {"statusCode": 500, "body": "Erro ao conectar ao banco de dados de Pedidos"}
    finally:
        if conn:
            conn.close()
            print("Conexão fechada.")

    # Configurações dos bancos de dados - Acompanhamento
    host = os.environ['ACOMPANHAMENTO_DB_HOST']
    database = os.environ['ACOMPANHAMENTO_DB_NAME']
    user = os.environ['ACOMPANHAMENTO_DB_USER']
    password = os.environ['ACOMPANHAMENTO_DB_PASSWORD']

    if len(pedidosParaRemover) != 0:
        # Conectar ao banco de dados - Acompanhamento
        try:
            conn = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )
            print("Conexão bem-sucedida!")
            cur = conn.cursor()

            # Primeira query: Excluir registros relacionados na tabela ItemPedido
            query_acompanhamento = cur.mogrify("""DELETE FROM public."Acompanhamento" WHERE "PedidoAggregateId" IN %s;""", pedidosParaRemover)

            # Executar a query para remover da tabela ItemPedido
            cur.execute(query_acompanhamento)

            # Aplicar as mudanças no banco de dados
            conn.commit()

            # Fechar cursor e conexão
            cur.close()
            print(f"Acompanhamentos removidos em {datetime.now()}.")
        except Exception as e:
            print(f"Erro ao conectar em Acompanhamentos: {e}")
            return {"statusCode": 500, "body": "Erro ao conectar ao banco de dados de Acompanhamentos"}
        finally:
            if conn:
                conn.close()
                print("Conexão fechada.")
    

    return {"statusCode": 200, "body": "Conexão bem-sucedida!"}