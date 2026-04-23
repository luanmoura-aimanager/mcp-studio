import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Define como o cliente vai iniciar o servidor.
# stdio = servidor roda como processo filho, comunicação via stdin/stdout.
# É o cliente quem dá spawn no servidor aqui — diferente do Inspector,
# onde o proxy fazia isso por nós.
server_params = StdioServerParameters(
    command="python",
    args=["server_01.py"],
)


async def main():
    # stdio_client é um async context manager que:
    # 1. Dá spawn no servidor com os params acima
    # 2. Retorna dois streams: read (do servidor) e write (para o servidor)
    async with stdio_client(server_params) as (read, write):
        # ClientSession é a camada do protocolo em cima dos streams crus.
        # Ela cuida de IDs de mensagem, correlação request/response, etc.
        async with ClientSession(read, write) as session:
            # Handshake MCP — mesma coisa que o "1. initialize" no Inspector
            await session.initialize()

            # ---- 1. Listar tools ----
            tools = await session.list_tools()
            print("Tools disponíveis:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description}")

            # ---- 2. Chamada válida ----
            print("\n[Teste 1] add(a=3, b=5) — tipos corretos")
            result = await session.call_tool("add", {"a": 3, "b": 5})
            print(f"  Resultado: {result}")

            # ---- 3. Chamada com string onde era pra ser int ----
            print("\n[Teste 2] add(a='3', b=5) — string onde deveria ser int")
            try:
                result = await session.call_tool("add", {"a": "3", "b": 5})
                print(f"  Resultado: {result}")
            except Exception as e:
                print(f"  Erro capturado: {type(e).__name__}: {e}")

            print("\n[Teste 3] multiply(a=3, b='4.5') — int e string onde deveria ser float")
            try:
                result = await session.call_tool("multiply", {"a": 3, "b": '4.5'})
                print(f"  Resultado: {result}")
            except Exception as e:
                print(f"  Erro capturado: {type(e).__name__}: {e}")

            print("\n[Teste 4] list_people — deve retornar uma lista de pessoas dado uma lista de strings com prefixo")
            try:
                result = await session.call_tool("list_people", {"prefix": "Nome:", "names_list": ["Nome:Bento", "Nome:Gaia", "Nome:Nilo"]})
                print(f"  Resultado: {result}")
            except Exception as e:
                print(f"  Erro capturado: {type(e).__name__}: {e}")

            print("\n[Teste 5] word_stats — deve retornar um dict contendo estatisticas sobre as palavras de um texto")
            try:
                result = await session.call_tool("word_stats", {"text": """
                    Um poema como um gole d'água bebido no escuro.
                    Como um pobre animal palpitando ferido.
                    Como pequenina moeda de prata perdida para sempre na
                    [floresta noturna.
                    Um poema sem outra angústia que a sua misteriosa condição
                    [de poema.
                    Triste.
                    Solitário.
                    Único.
                    Ferido de mortal beleza.
                    
                    Mario Quintana
                """})
                structured_result = result.structuredContent
                print(f"  Resultado:")
                print(f"  Palavras:      {structured_result['n_words']}")
                print(f"  Sem espaços:   {structured_result['n_chars__no_spaces']}")
                print(f"  Com espaços:   {structured_result['n_chars']}")
                print(f"  Maior palavra: {structured_result['longest_str']}")
                print(f"  Média chars:   {structured_result['avg_chars_overall_words']}")
            except Exception as e:
                print(f"  Erro capturado: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
