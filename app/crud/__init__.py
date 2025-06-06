from .clientes import (
    get_clientes,
    get_cliente,
    create_cliente,
    update_cliente,
    delete_cliente
)

from .produtos import (
    get_produto,
    get_produtos,
    create_produto,
    update_produto,
    delete_produto
)

from .estoque import (
    get_estoque,
    get_estoques,
    create_estoque,
    update_estoque,
    delete_estoque,
)

from .vendas import (
    get_vendas,
    get_venda,
    create_venda,
    update_venda,
    delete_venda,
    consolidar_venda_e_retornar_estoque,
)

from .feiras import (
    get_feira,
    get_feira_by_name,
    create_feira,
    get_feiras,
    update_feira,
    delete_feira,
    get_feira_by_name_and_date,
)

from .movimentacao_estoque import (
    create_movimentacao_estoque,
)