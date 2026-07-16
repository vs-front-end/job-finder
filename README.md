# Job Finder

Radar local de vagas remotas com busca, triagem e acompanhamento de candidaturas. O projeto
coleta oportunidades em fontes públicas, normaliza os anúncios, remove duplicatas e organiza
o fluxo entre vagas novas, salvas, candidaturas, processos e descartes.

## Principais recursos

- coleta agendada e execução manual das fontes;
- busca por cargo, empresa ou tecnologia;
- filtro determinístico de modalidade, senioridade, stack, idioma, região e moeda;
- separação de vagas compatíveis e vagas com região incerta;
- deduplicação entre fontes e revalidação dos links;
- descrição rica preservando parágrafos, listas, negrito e itálico;
- histórico manual de candidatura e etapas do processo;
- importação de vagas por URL com JSON-LD `JobPosting`;
- catálogo de plataformas automáticas e canais manuais;
- armazenamento local em SQLite, sem envio dos dados pessoais para terceiros.

## Stack

| Camada | Tecnologias |
|---|---|
| Backend | Python, FastAPI, Pydantic, HTTPX, Beautiful Soup e SQLite |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, Stellar UI e TanStack Query |
| Qualidade | Ruff, Pytest, ESLint, TypeScript e Vitest |

## Como funciona

1. Cada coletor consulta sua API, feed, ATS ou página pública.
2. O pipeline normaliza URLs, conteúdo, localização, remuneração e tecnologias.
3. Gates determinísticos eliminam vagas fora do perfil configurado.
4. As vagas restantes são deduplicadas e persistidas no SQLite.
5. A interface apresenta apenas o radar relevante e mantém as ações do usuário separadas.

O perfil padrão procura vagas remotas compatíveis com candidatos no Brasil e utiliza um filtro
negativo de senioridade: títulos explicitamente senior, staff, principal, lead, specialist ou
equivalentes são removidos, sem exigir que a vaga declare `junior` ou `mid-level`.

## Requisitos

- Python 3.12 ou superior;
- Node.js 20 ou superior;
- npm;
- `make` para utilizar os atalhos documentados abaixo.

## Instalação

```bash
git clone https://github.com/vs-front-end/job-finder.git
cd job-finder
make install
```

O comando cria `.venv`, instala o backend em modo editável e instala as dependências do
frontend.

## Executar em desenvolvimento

Em um terminal:

```bash
make backend
```

Em outro:

```bash
make frontend
```

A interface estará em `http://127.0.0.1:5173` e encaminhará `/api` para o backend em
`http://127.0.0.1:8787`.

## Executar o frontend compilado

```bash
make build
make backend
```

Depois, acesse `http://127.0.0.1:8787`. O FastAPI serve os arquivos gerados em `web/dist`.

## Configuração

As fontes, empresas, tecnologias, títulos e limites de coleta ficam em [`config.yaml`](config.yaml).
O arquivo é validado no startup; campos desconhecidos, expressões regulares inválidas ou valores
fora dos limites interrompem a inicialização com uma mensagem explícita.

Duas integrações oficiais são opcionais e ativadas por variáveis de ambiente:

```bash
export THE_MUSE_API_KEY="sua_chave"
export STARTUP_JOBS_API_KEY="sua_chave"
```

A triagem principal não depende de IA. A segunda opinião via Claude CLI permanece opcional:

```yaml
ia:
  enabled: true
  command: claude
  timeout_seconds: 90
```

Nesse modo, o processo usa a autenticação já existente no CLI e preserva a decisão
determinística caso o comando falhe ou retorne uma resposta inválida.

## Fontes

Entre as fontes disponíveis estão:

- Himalayas, Jobicy, Remote OK, Remotive, Arbeitnow e Hacker News;
- feeds de programação do We Work Remotely;
- Arc.dev, Y Combinator Jobs e Get on Board;
- APIs oficiais do The Muse e Startup Jobs, quando configuradas;
- boards públicos de Greenhouse, Lever e Ashby;
- feeds RSS adicionais e Google Alerts configuráveis;
- páginas individuais com JSON-LD `JobPosting`.

A estratégia e o estado de cada integração estão detalhados em
[`docs/SOURCES.md`](docs/SOURCES.md).

## API

A documentação OpenAPI fica disponível em `http://127.0.0.1:8787/docs`.

| Método | Endpoint | Finalidade |
|---|---|---|
| `GET` | `/api/jobs` | Listar e pesquisar vagas |
| `POST` | `/api/runs` | Iniciar uma coleta |
| `GET` | `/api/runs/status` | Consultar o estado da coleta |
| `GET` | `/api/sources` | Consultar a saúde das fontes |
| `POST` | `/api/jobs/import` | Importar uma vaga por URL |
| `POST` | `/api/jobs/{id}/events` | Registrar uma ação ou etapa |
| `PATCH` | `/api/jobs/{id}/eligibility` | Corrigir a elegibilidade regional |
| `GET` | `/api/platforms` | Listar plataformas acompanhadas |

## Qualidade

```bash
make lint
make test
make build
```

Também é possível executar a checagem de tipos do frontend isoladamente:

```bash
cd web
npm run type-check
```

## Estrutura

```text
app/
  api/          Rotas FastAPI
  collectors/   APIs, feeds, ATS e páginas públicas
  database/     Schema e repositório SQLite
  pipeline/     Normalização, filtros e deduplicação
  services/     Agendamento, importação e verificações
docs/           Matriz e estratégia das fontes
tests/          Testes do backend e dos coletores
web/            Aplicação React
config.yaml     Perfil e fontes do radar
```

O banco local é criado como `jobs.db` e usa WAL. Banco, ambiente virtual, dependências e builds
são ignorados pelo Git.
