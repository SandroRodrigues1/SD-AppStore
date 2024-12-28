import grpc
from concurrent import futures
import product_service_pb2
import product_service_pb2_grpc


class ProductService(product_service_pb2_grpc.ProductServiceServicer):
    def GetProducts(self, request, context):
        product1 = product_service_pb2.Product(
            id=1,
            name="Produto Exemplo 1",
            price=19.99,
            description="Descrição do Produto Exemplo 1",
            image="imagem1.jpg"
        )

        product2 = product_service_pb2.Product(
            id=2,
            name="Produto Exemplo 2",
            price=30.00,
            description="Descrição do Produto Exemplo 2",
            image="imagem2.jpg"
        )

        product_list = product_service_pb2.ProductList(products=[product1, product2])
        
        return product_list  

    def GetProductById(self, request, context):
        if request.id == 1:
            product = product_service_pb2.Product(
                id=1,
                name="Produto Exemplo 1",
                price=19.99,
                description="Descrição do Produto Exemplo 1",
                image="imagem1.jpg"
            )
            return product
        else:
            return product_service_pb2.Product() 

    def AddProduct(self, request, context):
        return product_service_pb2.ProductMessage(
            sucess=True,
            message="Produto adicionado com sucesso",
            error_code="",
            timestamp="2024-12-28T23:00:00"
        )

    def UpdateProduct(self, request, context):
        return product_service_pb2.ProductMessage(
            sucess=True,
            message="Produto atualizado com sucesso",
            error_code="",
            timestamp="2024-12-28T23:00:00"
        )

    def DeleteProduct(self, request, context):
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
