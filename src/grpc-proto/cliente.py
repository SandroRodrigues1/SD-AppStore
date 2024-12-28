import grpc
import product_service_pb2
import product_service_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = product_service_pb2_grpc.ProductServiceStub(channel)
        try:
            response = stub.GetProducts(product_service_pb2.Empty())
            print("GetProducts Response:", response)
        except grpc.RpcError as e:
            print("Error:", e)

if __name__ == "__main__":
    run()
