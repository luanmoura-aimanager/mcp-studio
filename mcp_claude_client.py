import asyncio
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def mcp_tools_to_anthropic(mcp_tools):
    """
    Recebe o objeto retornado por session.list_tools() e devolve
    a lista de tools no formato esperado pela API do Claude.
    """
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema,
        }
        for tool in mcp_tools.tools 
    ]

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["server_01.py"],
    )
    
    client = Anthropic()
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. Pega tools do servidor MCP e traduz
            mcp_tools = await session.list_tools()
            anthropic_tools = mcp_tools_to_anthropic(mcp_tools)
            
            # 2. Inicia o histórico com a pergunta do usuário
            user_question = "Quanto é 27 mais 15? E qual o resultado disso multiplicado por 2.5?"
            messages = [
                {"role": "user", "content": user_question}
            ]
            
            print(f"Usuário: {user_question}\n")
            
            # 3. ReAct loop
            while True:
                response = client.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=1024,
                    tools=anthropic_tools,
                    messages=messages,
                )
                
                # Sempre adiciona a resposta do assistant ao histórico
                messages.append({"role": "assistant", "content": response.content})
                
                # TODO 1: se stop_reason == "end_turn", imprime a resposta final
                #         (pega o texto do response.content) e dá break
                if response.stop_reason == "end_turn":
                    structured_response = ""
                    for block in response.content:
                        if block.type == "text":
                            structured_response += block.text + "\n"
                    print(f"Claude: {structured_response}\n")
                    break
                
                # TODO 2: se stop_reason == "tool_use", precisa:
                #         - encontrar o(s) bloco(s) de tool_use no response.content
                #         - para cada um, chamar session.call_tool(nome, args)
                #         - construir uma nova mensagem com role "user" contendo
                #           os tool_results, e adicionar ao messages
                elif response.stop_reason == "tool_use":
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            tool_name = block.name
                            tool_args = block.input
                            
                            # Chama a ferramenta no servidor MCP
                            tool_result = await session.call_tool(tool_name, tool_args)
                            
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": tool_result.content[0].text,
                            })

                    # Adiciona o resultado da ferramenta como uma nova mensagem do usuário
                    messages.append({
                        "role": "user",
                        "content": tool_results
                        #f"Resultado da ferramenta {tool_name}: {tool_result}"
                    })       
                
                # TODO 3: se for outro stop_reason qualquer, levanta erro
                #         (max_tokens, refusal, etc — não esperamos esses aqui)
                else:
                    raise Exception(f"Stop reason inesperada: {response.stop_reason}")


if __name__ == "__main__":
    asyncio.run(main())
