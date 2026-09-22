# APRESENTAÇÃO SOBRE TIMSORT

Projeto referente à apresentação do algoritmo de ordenação TimSort requisitado pelo professor Luis Henrique Sacchi, no curso de Bacharelado em Ciência da Computação pelo Instituto Federal de Educação, Ciência e Tecnologia (IFSP) — Campus Salto.
**Integrantes:**

- Eduardo Martins Corrêa
- Fábio Haruo de Freitas Nishioka
- Seren Iketani
- Yasmin Sampieri Tonello Cury

## Sumário

1. Como compilar
2. Como executar os benchmarks
3. Como executar os testes unitários

### 1 Como compilar

Para compilar o projeto, você precisará de:

1. um compilador, de preferência o [Gnu C Compiler (`gcc`)](https://gcc.gnu.org/);
2. o [`make`](https://www.gnu.org/software/make/);

> [!WARNING]
> Se você está no Linux, todos os pacotes já vêm instalados de fábrica. Caso você use Windows, terá de baixar as ferramentas manualmente. Procure sobre MSYS2 e adicione o `gcc.exe` ao `PATH` do sistema. A seguir, baixe o `choco` para baixar o `make`.

1. Clone o repositório:

```bash
git clone https://github.com/Haruo09/TimSortPresentation && cd TimSortPresentation
```

ou utilize o GitHub CLI:

```bash
gh repo clone Haruo09/TimSortPresentation && cd TimSortPresentation
```

A seguir, compile com o `make`:

```bash
make clean && make
```

A biblioteca estará compilada em um arquivo `.so` (ou `.dll`, no Windows) dentro da pasta `./build/lib/` e o processo de compilação gerará um arquivo executável em `./build/bin/`.

### 2 Como executar os benchmarks

Os benchmarks estão contidos dentro da pasta `./scripts`, e todos os arquivos de benchmark começam com `benchmark_*` em seus nomes.
Para executar os testes, primeiro é necessário baixar a ferramenta [`uv`](https://docs.astral.sh/uv/).

A seguir, crie um ambiente virtual executando:

```bash
uv venv
```

Ative o ambiente virtual executando:

```bash
source .venv/bin/activate
```

ou no Windows:

```bat
.\.venv\Scripts\activate
```

Instale as dependências:

```bash
uv pip install -r pyproject.toml
```

E, por fim, execute o benchmark desejado:

```bash
python ./scripts/benchmark_<benchmark_desejado>.py
```

### 3 Como executar os testes unitários

Caso não tenha instalado o `uv` ainda, volte na seção anterior e o faça.
Tendo todas as dependências carregadas e o ambiente virtual ativo, execute:

```bash
pytest ./tests -v
```
