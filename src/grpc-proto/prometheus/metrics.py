from prometheus_client import Counter, Histogram, Gauge
import time

class ProductServiceMetrics:

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

    # Métricas para gRPC
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


    # Métrica para conexões gRPC ativas
    GRPC_CONNECTIONS = Gauge(
        'grpc_connections', 
        'Number of active gRPC connections', 
        labelnames=['server']
    )

    # Métricas do sistema
    CPU_USAGE = Gauge(
        'process_cpu_usage', 
        'Current CPU usage in percent'
    )

    MEMORY_USAGE = Gauge(
        'process_memory_usage_bytes', 
        'Current memory usage in bytes'
    )

    # Métricas de contagem de requisições
    request_counter = Counter(
        "product_service_requests_total",
        "Total de requisições feitas ao serviço de produtos",
        labelnames=["method", "status", "path"]
    )

    # Métricas de contagem de produtos
    products_created = Counter(
        "product_service_products_created_total",
        "Total de produtos criados com sucesso no serviço"
    )

    products_fetched = Counter(
        "product_service_products_fetched_total",
        "Total de produtos recuperados com sucesso do serviço"
    )

    products_updated = Counter(
        "product_service_products_updated_total",
        "Total de produtos atualizados com sucesso no serviço"
    )

    products_deleted = Counter(
        "product_service_products_deleted_total",
        "Total de produtos deletados com sucesso do serviço"
    )

    # Métricas de erro
    create_errors = Counter(
        "product_service_create_errors_total",
        "Total de falhas ao criar produtos"
    )

    fetch_errors = Counter(
        "product_service_fetch_errors_total",
        "Total de falhas ao buscar produtos"
    )

    update_errors = Counter(
        "product_service_update_errors_total",
        "Total de falhas ao atualizar produtos"
    )

    delete_errors = Counter(
        "product_service_delete_errors_total",
        "Total de falhas ao deletar produtos"
    )

    # Métricas de latência (histograma)
    request_duration_histogram = Histogram(
        "product_service_request_duration_seconds",
        "Duração das requisições no serviço de produtos",
        labelnames=["method", "status", "path"]
    )

    # Métricas do banco de dados
    db_active_connections = Gauge(
        "database_active_connections",
        "Número de conexões ativas no banco de dados"
    )

    db_query_errors = Counter(
        "database_query_errors_total",
        "Número total de erros de consulta ao banco de dados"
    )

    # Métrica de verificação de saúde (health check)
    health_check_requests = Counter(
        "product_service_health_check_requests_total",
        "Total de requisições de verificação de saúde"
    )
