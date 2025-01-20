import grpc
import product_service_pb2
import product_service_pb2_grpc

def get_products(stub):
    try:
        response = stub.GetProducts(product_service_pb2.Empty())
        print("\n=== Lista de Produtos ===")
        if response.products:
            for product in response.products:
                print(f"ID: {product.id}, Nome: {product.name}, Preço: {product.price}, "
                      f"Descrição: {product.description}, Imagem: {product.image}")
        else:
            print("Nenhum produto encontrado.")
    except grpc.RpcError as e:
        print("Erro ao obter produtos:", e)

def get_product_by_id(stub):
    try:
        product_id = int(input("\nDigite o ID do produto que deseja buscar: "))
        product_request = product_service_pb2.ProductRequest(id=product_id)
        response = stub.GetProductById(product_request)
        if response.id:
            print(f"\n=== Produto Encontrado ===\nID: {response.id}, Nome: {response.name}, Preço: {response.price}, "
                  f"Descrição: {response.description}, Imagem: {response.image}")
        else:
            print("Produto não encontrado.")
    except grpc.RpcError as e:
        print("Erro ao obter produto:", e)

def add_product(stub):
    try:
        print("\n=== Adicionar Produto ===")
        name = input("Nome do produto: ")
        price = float(input("Preço do produto: "))
        description = input("Descrição do produto: ")
        image = input("URL da imagem do produto (opcional): ")

        new_product = product_service_pb2.Product(
            name=name,
            price=price,
            description=description,
            image=image or "N/A"
        )
        response = stub.AddProduct(new_product)
        print(f"Produto adicionado com sucesso: {response.message}")
    except grpc.RpcError as e:
        print("Erro ao adicionar produto:", e)

def update_product(stub):
    try:
        print("\n=== Atualizar Produto ===")
        product_id = int(input("ID do produto que deseja atualizar: "))
        name = input("Novo nome do produto: ")
        price = float(input("Novo preço do produto: "))
        description = input("Nova descrição do produto: ")
        image = input("Nova URL da imagem do produto (opcional): ")

        updated_product = product_service_pb2.Product(
            id=product_id,
            name=name,
            price=price,
            description=description,
            image=image or "N/A"
        )
        response = stub.UpdateProduct(updated_product)
        print(f"Produto atualizado com sucesso: {response.message}")
    except grpc.RpcError as e:
        print("Erro ao atualizar produto:", e)

def delete_product(stub):
    try:
        product_id = int(input("\nDigite o ID do produto que deseja deletar: "))
        product_to_delete = product_service_pb2.Product(id=product_id)
        response = stub.DeleteProduct(product_to_delete)
        print(f"Produto deletado com sucesso: {response.message}")
    except grpc.RpcError as e:
        print("Erro ao deletar produto:", e)

def menu():
    with grpc.insecure_channel('localhost:8080') as channel:
        stub = product_service_pb2_grpc.ProductServiceStub(channel)

        while True:
            print("\n=== Menu Principal ===")
            print("1. Ver todos os produtos")
            print("2. Buscar produto por ID")
            print("3. Adicionar produto")
            print("4. Atualizar produto")
            print("5. Deletar produto")
            print("6. Sair")
            
            choice = input("Escolha uma opção: ")
            
            if choice == "1":
                get_products(stub)
            elif choice == "2":
                get_product_by_id(stub)
            elif choice == "3":
                add_product(stub)
            elif choice == "4":
                update_product(stub)
            elif choice == "5":
                delete_product(stub)
            elif choice == "6":
                print("Encerrando o programa")
                break
            else:
                print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()
