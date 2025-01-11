import grpc
import time
from concurrent import futures
import product_service_pb2
import product_service_pb2_grpc
from database.database import create_connection  
from prometheus_client import start_http_server
from prometheus.metrics import ProductServiceMetrics  # Importando as métricas

class ProductService(product_service_pb2_grpc.ProductServiceServicer):

    def GetProducts(self, request, context):
        start_time = time.time()  # Iniciando o cronômetro para medir a duração da requisição
        try:
            connection = create_connection()
            if connection is None:
                ProductServiceMetrics.request_counter.labels(method="GetProducts", status="failure").inc()
                return product_service_pb2.ProductList()

            cursor = connection.cursor()
            cursor.execute("SELECT id, name, price, description, image FROM products")
            rows = cursor.fetchall()

            product_list = []
            for row in rows:
                product = product_service_pb2.Product(
                    id=row[0],
                    name=row[1],
                    price=row[2],
                    description=row[3],
                    image=row[4]
                )
                product_list.append(product)

            cursor.close()
            connection.close()

            ProductServiceMetrics.products_fetched.inc()  # Incrementando a contagem de produtos recuperados
            ProductServiceMetrics.request_counter.labels(method="GetProducts", status="success").inc()  # Sucesso
        except Exception as e:
            ProductServiceMetrics.request_counter.labels(method="GetProducts", status="failure").inc()  # Falha
            ProductServiceMetrics.fetch_errors.inc()  # Incrementa erro de busca
            raise e  # Relança a exceção

        duration = time.time() - start_time
        ProductServiceMetrics.request_duration_histogram.labels(method="GetProducts").observe(duration)  # Registra a duração da requisição
        return product_service_pb2.ProductList(products=product_list)

    def GetProductById(self, request, context):
        start_time = time.time()
        try:
            connection = create_connection()
            if connection is None:
                ProductServiceMetrics.request_counter.labels(method="GetProductById", status="failure").inc()
                return product_service_pb2.Product()

            cursor = connection.cursor()
            cursor.execute("SELECT id, name, price, description, image FROM products WHERE id = %s", (request.id,))
            row = cursor.fetchone()

            cursor.close()
            connection.close()

            if row:
                ProductServiceMetrics.products_fetched.inc()  # Produto recuperado
                ProductServiceMetrics.request_counter.labels(method="GetProductById", status="success").inc()  # Sucesso
            else:
                ProductServiceMetrics.request_counter.labels(method="GetProductById", status="failure").inc()  # Falha
        except Exception as e:
            ProductServiceMetrics.request_counter.labels(method="GetProductById", status="failure").inc()
            ProductServiceMetrics.fetch_errors.inc()  # Incrementa erro de busca
            raise e

        duration = time.time() - start_time
        ProductServiceMetrics.request_duration_histogram.labels(method="GetProductById").observe(duration)
        return product_service_pb2.Product(id=row[0], name=row[1], price=row[2], description=row[3], image=row[4]) if row else product_service_pb2.Product()

    def AddProduct(self, request, context):
        start_time = time.time()
        try:
            connection = create_connection()
            if connection is None:
                ProductServiceMetrics.request_counter.labels(method="AddProduct", status="failure").inc()
                return product_service_pb2.ProductMessage(
                    sucess=False,
                    message="Erro ao conectar ao banco de dados",
                    error_code="DB_CONNECTION_ERROR",
                    timestamp="2024-12-28T23:00:00"
                )

            cursor = connection.cursor()
            # Alterado para não passar o id, já que o MySQL gerará automaticamente
            cursor.execute(
                """INSERT INTO products (name, price, description, image) 
                VALUES (%s, %s, %s, %s)""",  # Removido o id da query
                (request.name, request.price, request.description, request.image)
            )
            connection.commit()

            cursor.close()
            connection.close()

            ProductServiceMetrics.products_created.inc()  # Incrementa o contador de produtos criados
            ProductServiceMetrics.request_counter.labels(method="AddProduct", status="success").inc()  # Sucesso
        except Exception as e:
            ProductServiceMetrics.request_counter.labels(method="AddProduct", status="failure").inc()  # Falha
            ProductServiceMetrics.create_errors.inc()  # Incrementa erro de criação
            raise e

        duration = time.time() - start_time
        ProductServiceMetrics.request_duration_histogram.labels(method="AddProduct").observe(duration)
        return product_service_pb2.ProductMessage(
            sucess=True,
            message="Produto adicionado com sucesso",
            error_code="",
            timestamp="2024-12-28T23:00:00"
        )

    def UpdateProduct(self, request, context):
        start_time = time.time()
        try:
            connection = create_connection()
            if connection is None:
                ProductServiceMetrics.request_counter.labels(method="UpdateProduct", status="failure").inc()
                return product_service_pb2.ProductMessage(
                    sucess=False,
                    message="Erro ao conectar ao banco de dados",
                    error_code="DB_CONNECTION_ERROR",
                    timestamp="2024-12-28T23:00:00"
                )

            cursor = connection.cursor()
            cursor.execute(
                """UPDATE products 
                SET name = %s, price = %s, description = %s, image = %s 
                WHERE id = %s""",
                (request.name, request.price, request.description, request.image, request.id)
            )
            connection.commit()

            cursor.close()
            connection.close()

            ProductServiceMetrics.products_updated.inc()  # Incrementa contador de produtos atualizados
            ProductServiceMetrics.request_counter.labels(method="UpdateProduct", status="success").inc()  # Sucesso
        except Exception as e:
            ProductServiceMetrics.request_counter.labels(method="UpdateProduct", status="failure").inc()  # Falha
            ProductServiceMetrics.update_errors.inc()  # Incrementa erro de atualização
            raise e

        duration = time.time() - start_time
        ProductServiceMetrics.request_duration_histogram.labels(method="UpdateProduct").observe(duration)
        return product_service_pb2.ProductMessage(
            sucess=True,
            message="Produto atualizado com sucesso",
            error_code="",
            timestamp="2024-12-28T23:00:00"
        )
    
    def DeleteProduct(self, request, context):
        try:
            # Conectando ao banco de dados
            connection = create_connection()
            if connection is None:
                return product_service_pb2.ProductMessage(
                    sucess=False,
                    message="Erro ao conectar ao banco de dados",
                    error_code="DB_CONNECTION_ERROR",
                    timestamp="2025-01-10T23:00:00"
                )
            
            cursor = connection.cursor()

            # Executando o comando DELETE
            cursor.execute("DELETE FROM products WHERE id = %s", (request.id,))
            connection.commit()

            # Verificando se algo foi deletado
            if cursor.rowcount == 0:
                return product_service_pb2.ProductMessage(
                    sucess=False,
                    message="Produto não encontrado para deletar.",
                    error_code="NOT_FOUND",
                    timestamp="2025-01-10T23:00:00"
                )

            cursor.close()
            connection.close()

            return product_service_pb2.ProductMessage(
                sucess=True,
                message="Produto deletado com sucesso.",
                error_code="",
                timestamp="2025-01-10T23:00:00"
            )
        except Exception as e:
            return product_service_pb2.ProductMessage(
                sucess=False,
                message=str(e),
                error_code="DELETE_ERROR",
                timestamp="2025-01-10T23:00:00"
            )



def serve():
    try:
        print("Iniciando o servidor...")
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        product_service_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
        server.add_insecure_port('[::]:8080')
        print("Servidor iniciado na porta 8080...")

        start_http_server(9091)  # Inicia o servidor Prometheus
        server.start()
        server.wait_for_termination()
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")

if __name__ == "__main__":
    serve()
