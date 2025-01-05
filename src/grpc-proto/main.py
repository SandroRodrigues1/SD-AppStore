import grpc
from concurrent import futures
import product_service_pb2
import product_service_pb2_grpc
from database.database import create_connection  

class ProductService(product_service_pb2_grpc.ProductServiceServicer):

    def GetProducts(self, request, context):
        connection = create_connection()
        if connection is None:
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

        return product_service_pb2.ProductList(products=product_list)

    def GetProductById(self, request, context):
        connection = create_connection()
        if connection is None:
            return product_service_pb2.Product()

        cursor = connection.cursor()
        cursor.execute("SELECT id, name, price, description, image FROM products WHERE id = %s", (request.id,))
        row = cursor.fetchone()

        cursor.close()
        connection.close()

        if row:
            return product_service_pb2.Product(
                id=row[0],
                name=row[1],
                price=row[2],
                description=row[3],
                image=row[4]
            )
        else:
            return product_service_pb2.Product()

    def AddProduct(self, request, context):
        connection = create_connection()
        if connection is None:
            return product_service_pb2.ProductMessage(
                sucess=False,
                message="Erro ao conectar ao banco de dados",
                error_code="DB_CONNECTION_ERROR",
                timestamp="2024-12-28T23:00:00"
            )

        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO products (id, name, price, description, image) 
               VALUES (%s, %s, %s, %s, %s)""",
            (request.id, request.name, request.price, request.description, request.image)
        )
        connection.commit()

        cursor.close()
        connection.close()

        return product_service_pb2.ProductMessage(
            sucess=True,
            message="Produto adicionado com sucesso",
            error_code="",
            timestamp="2024-12-28T23:00:00"
        )

    def UpdateProduct(self, request, context):
        connection = create_connection()
        if connection is None:
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

        return product_service_pb2.ProductMessage(
            sucess=True,
            message="Produto atualizado com sucesso",
            error_code="",
            timestamp="2024-12-28T23:00:00"
        )

    def DeleteProduct(self, request, context):
        connection = create_connection()
        if connection is None:
            return product_service_pb2.ProductMessage(
                sucess=False,
                message="Erro ao conectar ao banco de dados",
                error_code="DB_CONNECTION_ERROR",
                timestamp="2024-12-28T23:00:00"
            )

        cursor = connection.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s", (request.id,))
        connection.commit()

        cursor.close()
        connection.close()

        return product_service_pb2.ProductMessage(
            sucess=True,
            message="Produto deletado com sucesso",
            error_code="",
            timestamp="2024-12-28T23:00:00"
        )


def serve():
    try:
        print("Iniciando o servidor...")
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        product_service_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
        server.add_insecure_port('[::]:8080')
        print("Servidor iniciado na porta 8080...")
        server.start()
        server.wait_for_termination()
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")


if __name__ == "__main__":
    serve()

