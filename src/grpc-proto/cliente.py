import grpc
import product_service_pb2
import product_service_pb2_grpc

def run():

    with grpc.insecure_channel('localhost:8080') as channel:
        stub = product_service_pb2_grpc.ProductServiceStub(channel)
        try:
            response = stub.GetProducts(product_service_pb2.Empty())
            print("GetProducts Response:")
            for product in response.products:
                print(f"ID: {product.id}, Name: {product.name}, Price: {product.price}, Description: {product.description}, Image: {product.image}")
        
        except grpc.RpcError as e:
            print("Error:", e)

if __name__ == "__main__":
    run()
