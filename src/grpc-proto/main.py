import grpc
import time
from concurrent import futures
import product_service_pb2
import product_service_pb2_grpc
from database.database import create_connection  
from prometheus_client import start_http_server
from prometheus.metrics import ProductServiceMetrics  # Importando as métricas do arquivo metrics.py
from prometheus_client import Counter, Histogram, Gauge  # Importando métricas adicionais

# Definindo métricas adicionais
REQUEST_COUNT = Counter(
    'http_request_total', 
    'Total HTTP Requests', 
    labelnames=['method', 'status', 'path']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP Request Duration', 
    labelnames=['method', 'status', 'path']
)

REQUEST_IN_PROGRESS = Gauge(
    'http_requests_in_progress', 
    'HTTP Requests in progress', 
    labelnames=['method', 'path']
)

GRPC_REQUEST_COUNT = Counter(
    'grpc_request_total', 
    'Total gRPC Requests', 
    labelnames=['method', 'status']
)

GRPC_REQUEST_LATENCY = Histogram(
    'grpc_request_duration_seconds', 
    'gRPC Request Duration', 
    labelnames=['method', 'status']
)

GRPC_CONNECTIONS = Gauge(
    'grpc_connections', 
    'Number of active gRPC connections', 
    labelnames=['server']
)

CPU_USAGE = Gauge(
    'process_cpu_usage', 
    'Current CPU usage in percent'
)

MEMORY_USAGE = Gauge(
    'process_memory_usage_bytes', 
    'Current memory usage in bytes'
)

request_counter = Counter(
    "product_service_requests_total",
    "Total de requisições feitas ao serviço de produtos",
    labelnames=["method", "status", "path"]
)

class ProductService(product_service_pb2_grpc.ProductServiceServicer):

    def GetProducts(self, request, context):
        print("Starting the GetProducts")
        start_time = time.time() 
        REQUEST_IN_PROGRESS.labels(method="GetProducts", path="/GetProducts").inc() 
        try:
            print("Starting the connection to the database!")
            connection = create_connection()
            if connection is None:
                print("The connection has failed!")
                REQUEST_COUNT.labels(method="GetProducts", status="failure", path="/GetProducts").inc()
                REQUEST_IN_PROGRESS.labels(method="GetProducts", path="/GetProducts").dec()
                return product_service_pb2.ProductList()

            cursor = connection.cursor()
            cursor.execute("SELECT id, name, price, description, image FROM products")
            rows = cursor.fetchall()

            product_list = []
            for row in rows:
                product = product_service_pb2.Product(
                    id=row[0],
                    name=row[1],
                    price=round(row[2], 2),  # Garantir duas casas decimais
                    description=row[3],
                    image=row[4]
                )
                print(product.price)
                product_list.append(product)

            cursor.close()
            connection.close()

            ProductServiceMetrics.products_fetched.inc(len(product_list))  
            REQUEST_COUNT.labels(method="GetProducts", status="success", path="/GetProducts").inc()  
        except Exception as e:
            REQUEST_COUNT.labels(method="GetProducts", status="failure", path="/GetProducts").inc()  
            ProductServiceMetrics.fetch_errors.inc()  
            print(e)
            raise e  
        finally:
            REQUEST_IN_PROGRESS.labels(method="GetProducts", path="/GetProducts").dec()  

        duration = time.time() - start_time
        REQUEST_LATENCY.labels(method="GetProducts", status="success", path="/GetProducts").observe(duration)  # Latência
        return product_service_pb2.ProductList(products=product_list)

    def GetProductById(self, request, context):
        start_time = time.time()
        REQUEST_IN_PROGRESS.labels(method="GetProductById", path="/GetProductById").inc()
        try:
            connection = create_connection()
            if connection is None:
                REQUEST_COUNT.labels(method="GetProductById", status="failure", path="/GetProductById").inc()
                REQUEST_IN_PROGRESS.labels(method="GetProductById", path="/GetProductById").dec()
                return product_service_pb2.Product()

            cursor = connection.cursor()
            cursor.execute("SELECT id, name, price, description, image FROM products WHERE id = %s", (request.id,))
            row = cursor.fetchone()

            cursor.close()
            connection.close()

            if row:
                ProductServiceMetrics.products_fetched.inc()  
                REQUEST_COUNT.labels(method="GetProductById", status="success", path="/GetProductById").inc()  # Sucesso
            else:
                REQUEST_COUNT.labels(method="GetProductById", status="failure", path="/GetProductById").inc()  # Falha
        except Exception as e:
            REQUEST_COUNT.labels(method="GetProductById", status="failure", path="/GetProductById").inc()  # Falha
            ProductServiceMetrics.fetch_errors.inc()  
            print(e)
            raise e
        finally:
            REQUEST_IN_PROGRESS.labels(method="GetProductById", path="/GetProductById").dec()

        duration = time.time() - start_time
        REQUEST_LATENCY.labels(method="GetProductById", status="success", path="/GetProductById").observe(duration)  # Latência
        return product_service_pb2.Product(id=row[0], name=row[1], price=round(row[2], 2), description=row[3], image=row[4]) if row else product_service_pb2.Product()

    def AddProduct(self, request, context):
        start_time = time.time()
        REQUEST_IN_PROGRESS.labels(method="AddProduct", path="/AddProduct").inc()
        try:
            connection = create_connection()
            if connection is None:
                REQUEST_COUNT.labels(method="AddProduct", status="failure", path="/AddProduct").inc()
                REQUEST_IN_PROGRESS.labels(method="AddProduct", path="/AddProduct").dec()
                return product_service_pb2.ProductMessage(
                    sucess=False,
                    message="Erro ao conectar ao banco de dados",
                    error_code="DB_CONNECTION_ERROR",
                    timestamp="2024-12-28T23:00:00"
                )

            cursor = connection.cursor()
            cursor.execute(
                """INSERT INTO products (name, price, description, image) 
                VALUES (%s, %s, %s, %s)""",  # Removido o id da query
                (request.name, round(request.price, 2), request.description, request.image)  # Arredondando preço
            )
            connection.commit()

            cursor.close()
            connection.close()

            ProductServiceMetrics.products_created.inc()  
            REQUEST_COUNT.labels(method="AddProduct", status="success", path="/AddProduct").inc()  # Sucesso
        except Exception as e:
            REQUEST_COUNT.labels(method="AddProduct", status="failure", path="/AddProduct").inc()  # Falha
            ProductServiceMetrics.create_errors.inc()  
            print(e)
            raise e
        finally:
            REQUEST_IN_PROGRESS.labels(method="AddProduct", path="/AddProduct").dec()

        duration = time.time() - start_time
        REQUEST_LATENCY.labels(method="AddProduct", status="success", path="/AddProduct").observe(duration)  # Latência
        return product_service_pb2.ProductMessage(
            sucess=True,
            message="Produto adicionado com sucesso",
            error_code="",
            timestamp="2024-12-28T23:00:00"
        )

    def UpdateProduct(self, request, context):
        start_time = time.time()
        REQUEST_IN_PROGRESS.labels(method="UpdateProduct", path="/UpdateProduct").inc()
        try:
            connection = create_connection()
            if connection is None:
                REQUEST_COUNT.labels(method="UpdateProduct", status="failure", path="/UpdateProduct").inc()
                REQUEST_IN_PROGRESS.labels(method="UpdateProduct", path="/UpdateProduct").dec()
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
                (request.name, round(request.price, 2), request.description, request.image, request.id)  # Arredondando preço
            )
            connection.commit()

            cursor.close()
            connection.close()

            ProductServiceMetrics.products_updated.inc()  
            REQUEST_COUNT.labels(method="UpdateProduct", status="success", path="/UpdateProduct").inc()  # Sucesso
        except Exception as e:
            REQUEST_COUNT.labels(method="UpdateProduct", status="failure", path="/UpdateProduct").inc()  # Falha
            ProductServiceMetrics.update_errors.inc()  
            print(e)
            raise e
        finally:
            REQUEST_IN_PROGRESS.labels(method="UpdateProduct", path="/UpdateProduct").dec()

        duration = time.time() - start_time
        REQUEST_LATENCY.labels(method="UpdateProduct", status="success", path="/UpdateProduct").observe(duration)  # Latência
        return product_service_pb2.ProductMessage(
            sucess=True,
            message="Produto atualizado com sucesso",
            error_code="",
            timestamp="2024-12-28T23:00:00"
        )

    def DeleteProduct(self, request, context):
        REQUEST_IN_PROGRESS.labels(method="DeleteProduct", path="/DeleteProduct").inc()
        try:
            # Conectando a base de dados
            connection = create_connection()
            if connection is None:
                REQUEST_COUNT.labels(method="DeleteProduct", status="failure", path="/DeleteProduct").inc()
                REQUEST_IN_PROGRESS.labels(method="DeleteProduct", path="/DeleteProduct").dec()
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
                REQUEST_COUNT.labels(method="DeleteProduct", status="failure", path="/DeleteProduct").inc()
                REQUEST_IN_PROGRESS.labels(method="DeleteProduct", path="/DeleteProduct").dec()
                return product_service_pb2.ProductMessage(
                    sucess=False,
                    message="Produto não encontrado para deletar.",
                    error_code="NOT_FOUND",
                    timestamp="2025-01-10T23:00:00"
                )

            cursor.close()
            connection.close()

            ProductServiceMetrics.products_deleted.inc()  
            REQUEST_COUNT.labels(method="DeleteProduct", status="success", path="/DeleteProduct").inc()  # Sucesso
        except Exception as e:
            REQUEST_COUNT.labels(method="DeleteProduct", status="failure", path="/DeleteProduct").inc()  # Falha
            ProductServiceMetrics.delete_errors.inc()  
            return product_service_pb2.ProductMessage(
                sucess=False,
                message=str(e),
                error_code="DELETE_ERROR",
                timestamp="2025-01-10T23:00:00"
            )
        finally:
            REQUEST_IN_PROGRESS.labels(method="DeleteProduct", path="/DeleteProduct").dec()

        return product_service_pb2.ProductMessage(
            sucess=True,
            message="Produto deletado com sucesso.",
            error_code="",
            timestamp="2025-01-10T23:00:00"
        )


def serve():
    try:
        print("Iniciando o servidor...")
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        product_service_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
        server.add_insecure_port('[::]:8080')
        print("Servidor iniciado na porta 8080...")

        start_http_server(9100)  
        server.start()
        server.wait_for_termination()
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")

if __name__ == "__main__":
    serve()
