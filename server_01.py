from mcp.server.fastmcp import FastMCP
import numpy as np
import sys

# Cria uma instância de servidor MCP com um nome identificador.
# Esse nome aparece para o cliente na hora do handshake.
mcp = FastMCP("demo-server")


# O decorador @mcp.tool() registra a função como uma Tool MCP.
# Igual em espírito ao @tool do LangChain: a docstring vira a descrição
# que o LLM vê, e os type hints viram o schema de input.
@mcp.tool()
def add(a: int, b: int) -> int:
    """Soma dois números inteiros."""
    return a + b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiplica dois números floats."""
    return a * b


@mcp.tool()
def greet(name: str) -> str:
    """Retorna uma saudação personalizada para o nome recebido."""
    return f"Olá, {name}! Bem-vindo ao primeiro MCP server."


@mcp.tool()
def list_people(prefix: str, names_list: list[str]) -> list[str]:
    """Deve listar os nomes das pessoas, removendo o prefixo de cada nome na lista."""
    return [name.split(prefix)[1] for name in names_list]


@mcp.tool()
def word_stats(text: str) -> dict[str, object]:
    """retorna um dicionário com estatísticas: número de palavras, 
    número de caracteres (com e sem espaços), palavra mais longa,
    e média de caracteres por palavra."""
    splited_text = text.split()
    chars_by_word = []
    text__no_spaces = ""

    longest_word, longest_word_n_chars = "", 0

    for word in splited_text:
        text__no_spaces += word
        if len(word) > longest_word_n_chars:
            longest_word_n_chars = len(word)
            longest_word = word
        chars_by_word.append(len(word))

    stats_dict = dict()
    stats_dict["n_words"] = len(splited_text)
    stats_dict["n_chars"] = len(text)
    stats_dict["n_chars__no_spaces"] = len(text__no_spaces)
    stats_dict["longest_str"] = longest_word
    stats_dict["avg_chars_overall_words"] = float(np.mean(chars_by_word))
    print(f"DEBUG tipos: { {k: type(v).__name__ for k, v in stats_dict.items()} }", file=sys.stderr)
    return stats_dict

# Entry point padrão. Sem argumento, .run() usa transport stdio
# (servidor se comunica via stdin/stdout do processo).
# Para desenvolvimento, a gente nem vai chamar esse arquivo diretamente —
# vai usar `mcp dev server_01.py` que abre o Inspector automaticamente.
if __name__ == "__main__":
    mcp.run()
