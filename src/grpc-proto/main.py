import grpc
import time
from concurrent import futures
import product_service_pb2
import product_service_pb2_grpc
from database.database import create_connection  
from prometheus_client import start_http_server
from prometheus_client import Counter, Histogram, Gauge
from metrics import ProductServiceMetrics  # Importando as métricas do arquivo metrics.py
import psutil  # Para pegar as métricas de uso de CPU e memória

class ProductService(product_service_pb2_grpc.ProductServiceServicer):

    # Método para coletar métricas do sistema
    def collect_system_metrics(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().used

        ProductServiceMetrics.CPU_USAGE.set(cpu_usage)  # Atualiza a métrica de CPU
        ProductServiceMetrics.MEMORY_USAGE.set(memory_usage)  # Atualiza a métrica de memória

    def GetProducts(self, request, context):
        print("Starting the GetProducts")
        start_time = time.time()  # Iniciando o cronômetro para medir a duração da requisição

        # Indicando que uma requisição HTTP está em andamento
        ProductServiceMetrics.REQUEST_IN_PROGRESS.labels(method="GET", path="/GetProducts").inc()

        try:
            print("Starting the connection to the database!")
            connection = create_connection()
            if connection is None:
                print("The connection has failed!")
                ProductServiceMetrics.REQUEST_COUNT.labels(method="GET", status="failure", path="/GetProducts").inc()
                ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="GetProducts", status="failure").inc()  # gRPC falhou
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

            ProductServiceMetrics.REQUEST_COUNT.labels(method="GET", status="success", path="/GetProducts").inc()  # Sucesso
            ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="GetProducts", status="success").inc()  # gRPC sucesso
        except Exception as e:
            ProductServiceMetrics.REQUEST_COUNT.labels(method="GET", status="failure", path="/GetProducts").inc()  # Falha
            ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="GetProducts", status="failure").inc()  # gRPC falhou
            print(e)
            raise e  # Relança a exceção

        duration = time.time() - start_time
        ProductServiceMetrics.REQUEST_LATENCY.labels(method="GET", status="success", path="/GetProducts").observe(duration)  # Latência HTTP
        ProductServiceMetrics.GRPC_REQUEST_LATENCY.labels(method="GetProducts", status="success").observe(duration)  # Latência gRPC
        ProductServiceMetrics.REQUEST_IN_PROGRESS.labels(method="GET", path="/GetProducts").dec()  # Finaliza a requisição HTTP

        return product_service_pb2.ProductList(products=product_list)

    def GetProductById(self, request, context):
        start_time = time.time()
        ProductServiceMetrics.REQUEST_IN_PROGRESS.labels(method="GET", path="/GetProductById").inc()

        try:
            connection = create_connection()
            if connection is None:
                ProductServiceMetrics.REQUEST_COUNT.labels(method="GET", status="failure", path="/GetProductById").inc()
                ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="GetProductById", status="failure").inc()
                return product_service_pb2.Product()

            cursor = connection.cursor()
            cursor.execute("SELECT id, name, price, description, image FROM products WHERE id = %s", (request.id,))
            row = cursor.fetchone()

            cursor.close()
            connection.close()

            if row:
                ProductServiceMetrics.REQUEST_COUNT.labels(method="GET", status="success", path="/GetProductById").inc()  # Sucesso
                ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="GetProductById", status="success").inc()  # Sucesso gRPC
            else:
                ProductServiceMetrics.REQUEST_COUNT.labels(method="GET", status="failure", path="/GetProductById").inc()  # Falha
                ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="GetProductById", status="failure").inc()  # Falha gRPC
        except Exception as e:
            ProductServiceMetrics.REQUEST_COUNT.labels(method="GET", status="failure", path="/GetProductById").inc()  # Falha
            ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="GetProductById", status="failure").inc()  # Falha gRPC
            print(e)
            raise e

        duration = time.time() - start_time
        ProductServiceMetrics.REQUEST_LATENCY.labels(method="GET", status="success", path="/GetProductById").observe(duration)  # Latência HTTP
        ProductServiceMetrics.GRPC_REQUEST_LATENCY.labels(method="GetProductById", status="success").observe(duration)  # Latência gRPC
        ProductServiceMetrics.REQUEST_IN_PROGRESS.labels(method="GET", path="/GetProductById").dec()  # Finaliza a requisição HTTP
        return product_service_pb2.Product(id=row[0], name=row[1], price=row[2], description=row[3], image=row[4]) if row else product_service_pb2.Product()

    # O método AddProduct também foi alterado da mesma forma
    def AddProduct(self, request, context):
        start_time = time.time()
        ProductServiceMetrics.REQUEST_IN_PROGRESS.labels(method="POST", path="/AddProduct").inc()

        try:
            connection = create_connection()
            if connection is None:
                ProductServiceMetrics.REQUEST_COUNT.labels(method="POST", status="failure", path="/AddProduct").inc()
                ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="AddProduct", status="failure").inc()
                return product_service_pb2.ProductMessage(sucess=False)

            cursor = connection.cursor()
            cursor.execute(
                """INSERT INTO products (name, price, description, image) VALUES (%s, %s, %s, %s)""",
                (request.name, request.price, request.description, request.image)
            )
            connection.commit()

            cursor.close()
            connection.close()

            ProductServiceMetrics.REQUEST_COUNT.labels(method="POST", status="success", path="/AddProduct").inc()  # Sucesso
            ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="AddProduct", status="success").inc()  # Sucesso gRPC
        except Exception as e:
            ProductServiceMetrics.REQUEST_COUNT.labels(method="POST", status="failure", path="/AddProduct").inc()  # Falha
            ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="AddProduct", status="failure").inc()  # Falha gRPC
            print(e)
            raise e

        duration = time.time() - start_time
        ProductServiceMetrics.REQUEST_LATENCY.labels(method="POST", status="success", path="/AddProduct").observe(duration)  # Latência HTTP
        ProductServiceMetrics.GRPC_REQUEST_LATENCY.labels(method="AddProduct", status="success").observe(duration)  # Latência gRPC
        ProductServiceMetrics.REQUEST_IN_PROGRESS.labels(method="POST", path="/AddProduct").dec()  # Finaliza a requisição HTTP

        return product_service_pb2.ProductMessage(sucess=True)

    def UpdateProduct(self, request, context):
        start_time = time.time()
        ProductServiceMetrics.REQUEST_IN_PROGRESS.labels(method="PUT", path="/UpdateProduct").inc()

        try:
            connection = create_connection()
            if connection is None:
                ProductServiceMetrics.REQUEST_COUNT.labels(method="PUT", status="failure", path="/UpdateProduct").inc()
                ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="UpdateProduct", status="failure").inc()
                return product_service_pb2.ProductMessage(sucess=False)

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

            ProductServiceMetrics.REQUEST_COUNT.labels(method="PUT", status="success", path="/UpdateProduct").inc()  # Sucesso
            ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="UpdateProduct", status="success").inc()  # Sucesso gRPC
        except Exception as e:
            ProductServiceMetrics.REQUEST_COUNT.labels(method="PUT", status="failure", path="/UpdateProduct").inc()  # Falha
            ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="UpdateProduct", status="failure").inc()  # Falha gRPC
            print(e)
            raise e

        duration = time.time() - start_time
        ProductServiceMetrics.REQUEST_LATENCY.labels(method="PUT", status="success", path="/UpdateProduct").observe(duration)  # Latência HTTP
        ProductServiceMetrics.GRPC_REQUEST_LATENCY.labels(method="UpdateProduct", status="success").observe(duration)  # Latência gRPC
        ProductServiceMetrics.REQUEST_IN_PROGRESS.labels(method="PUT", path="/UpdateProduct").dec()  # Finaliza a requisição HTTP

        return product_service_pb2.ProductMessage(sucess=True)

    def DeleteProduct(self, request, context):
        start_time = time.time()
        ProductServiceMetrics.REQUEST_IN_PROGRESS.labels(method="DELETE", path="/DeleteProduct").inc()

        try:
            connection = create_connection()
            if connection is None:
                ProductServiceMetrics.REQUEST_COUNT.labels(method="DELETE", status="failure", path="/DeleteProduct").inc()
                ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="DeleteProduct", status="failure").inc()
                return product_service_pb2.ProductMessage(sucess=False)

            cursor = connection.cursor()
            cursor.execute("DELETE FROM products WHERE id = %s", (request.id,))
            connection.commit()

            cursor.close()
            connection.close()

            ProductServiceMetrics.REQUEST_COUNT.labels(method="DELETE", status="success", path="/DeleteProduct").inc()  # Sucesso
            ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="DeleteProduct", status="success").inc()  # Sucesso gRPC
        except Exception as e:
            ProductServiceMetrics.REQUEST_COUNT.labels(method="DELETE", status="failure", path="/DeleteProduct").inc()  # Falha
            ProductServiceMetrics.GRPC_REQUEST_COUNT.labels(method="DeleteProduct", status="failure").inc()  # Falha gRPC
            print(e)
            raise e

        duration = time.time() - start_time
        ProductServiceMetrics.REQUEST_LATENCY.labels(method="DELETE", status="success", path="/DeleteProduct").observe(duration)  # Latência HTTP
        ProductServiceMetrics.GRPC_REQUEST_LATENCY.labels(method="DeleteProduct", status="success").observe(duration)  # Latência gRPC
        ProductServiceMetrics.REQUEST_IN_PROGRESS.labels(method="DELETE", path="/DeleteProduct").dec()  # Finaliza a requisição HTTP

        return product_service_pb2.ProductMessage(sucess=True)

def serve():
    try:
        print("Iniciando o servidor...")
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        product_service_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
        server.add_insecure_port('[::]:8080')
        print("Servidor iniciado na porta 8080...")

        start_http_server(9100)  # Iniciando o servidor HTTP para expor as métricas
        server.start()
        server.wait_for_termination()
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")

if __name__ == "__main__":
    serve()
