# Coffeechain

O projeto Coffeechain propõe uma solução tecnológica para rastrear e gerenciar informações da produção de café desde a origem até o comprador final. Ele utiliza uma arquitetura em camadas que integra blockchain, responsável por armazenar dados de safra de forma segura e imutável, e uma IA Sumarizadora, que gera relatórios automáticos e históricos acessíveis aos compradores.
A camada de RAG (Retrieval-Augmented Generation) atua como intermediária, filtrando e estruturando as informações antes de chegarem à IA, o que permite consultas mais rápidas, precisas e contextualizadas sobre os registros do sistema.

## Justificativa

A rastreabilidade do café tornou-se uma necessidade diante das novas exigências do mercado europeu por origem comprovada e transparência nas cadeias produtivas. Nesse contexto, o uso de blockchain surge como meio de registrar dados de forma imutável e auditável, enquanto IA e RAG possibilitam análises mais ágeis e inteligentes sobre as informações da safra, conectando tecnologia, confiança e sustentabilidade no setor cafeeiro.

## Arquitetura

O tipo arquitetural escolhido foi a arquitetura em camadas.

#### Camada de Usuários e Interface
 - Usuários: Fiscais / Produtores, Compradores.
 - Interface: Frontend.
 - Função: Inserir dados, consultar rastreabilidade, visualizar relatórios.

#### Camada de Serviços Distribuídos
 - Componentes: API Gateway, sincronização de dados, autenticação/autorização.
 - Função: Roteamento de requisições, controle de acesso, comunicação entre microserviços, sincronização entre os nós da blockchain.

#### Camada de Inteligência Artificial
 - IA Sumarizadora
    - Atua como ponte convertendo a entrada do usuário em uma query na blockchain.

#### Camada de Blockchain e Dados
 - Blockchain:
    - Registra blocos de dados da safra, garantindo imutabilidade.
    - Rede de nós distribuídos em containers backend.
    - Bancos de dados auxiliares: SQL / NoSQL, banco vetorial para consultas RAG.

#### Camada de Filtragem e Sumarização (RAG)
 - Filtra, resume e formata dados do usúario para alimentar a IA.

#### Diagrama Arquitetural

![Image](./assets/Arquitetura.jpg)

## Autores

[Otávio Sbampato Andrade](https://github.com/otaviosbampato)
[Isac Gonçalves Cunha](https://github.com/isaccunha)
[Gabriel Coelho Costa](https://github.com/gabrielzinCoelho)
[Paulo Henrique Ribeiro Alves](https://github.com/paulohenrique64)