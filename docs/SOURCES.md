# Matriz de fontes

Pesquisa técnica revisada em 16 de julho de 2026. O Job Finder só automatiza páginas
públicas sem login e integrações que permitem esse uso. Toda coleta continua sujeita aos
termos e limites da fonte.

| Fonte | Modo no Job Finder | Busca aplicada |
|---|---|---|
| Himalayas | API pública, ativa | termos técnicos, ordem recente e corte local de 7 dias |
| Remote OK | API pública, ativa | feed recente e pós-filtro técnico/geográfico |
| We Work Remotely | RSS público, ativo | cinco feeds específicos de programação |
| Remotive | API pública, ativa | categoria `software-dev` |
| Arc.dev | página pública estruturada, experimental e ativa | tags React, TypeScript, JavaScript, Node.js, Python e full stack; detalhes apenas dos últimos 7 dias |
| Y Combinator Jobs | página pública estruturada, experimental e ativa | rota Software Engineer + Remote; detalhes apenas dos últimos 7 dias |
| The Muse | API oficial pronta, aguardando chave | categoria Software Engineering, modalidade remota e corte local de 7 dias |
| Get on Board | HTML público estruturado, ativo | programação remota; detalhes, região, data e salário por vaga |
| Startup Jobs | API oficial pronta, aguardando chave | remoto + engineering; a API já retorna somente os últimos 14 dias |
| Wellfound | manual | busca pública é bloqueada para automação; usar perfil/alertas |
| Welcome to the Jungle / Otta | manual | pesquisa de vagas exige sessão |
| Toptal | perfil manual | rede de talentos, sem feed público de oportunidades |
| Turing | perfil manual | matching privado; vagas corporativas da Turing não representam o marketplace |
| Crossover | manual | catálogo público é uma SPA sem API pública documentada e estável |
| Terminal | perfil manual | matching por perfil; lista pública não oferece feed estável |
| VanHack | perfil manual | oportunidades dependem de conta/perfil |
| Remote.com Jobs | manual | API pública da Remote é de RH, não uma API de busca de vagas |
| Braintrust | perfil manual | marketplace de talentos sem feed público documentado |
| Lemon.io | perfil manual | matching privado de desenvolvedores |
| Gun.io | perfil manual | página pública não informa data confiável por oportunidade |
| LinkedIn Jobs | alertas manuais | sem scraping ou conta automatizada; JobSpy permanece desligado |
| Indeed | alertas manuais | APIs documentadas são para parceiros/publicação, não busca pública geral |
| GitHub agregados | RSS/URL configurável | não existe mais um GitHub Jobs oficial; aceitar apenas feeds ou listas indicados no config |

Outras fontes já ativas: Jobicy, Arbeitnow, Hacker News Who Is Hiring e páginas diretas de
empresas em Greenhouse, Lever e Ashby. Salário desconhecido não elimina uma vaga; moeda BRL
explicitamente informada é rejeitada, enquanto USD, EUR, GBP, CAD, CHF, AUD e NZD são
preferidas. Anúncios claramente escritos em idiomas diferentes de inglês ou português são
removidos pelo filtro determinístico.

A página **Plataformas** mantém o catálogo completo de 50 canais: fontes automáticas, redes
de talentos, boards regionais e ATS planejados. O estado dos perfis manuais é salvo no SQLite
como pendente, configurado/revisado, revisão necessária ou ignorado.

Para ativar as APIs depois de criar as chaves gratuitas:

```bash
export STARTUP_JOBS_API_KEY="sj_..."
export THE_MUSE_API_KEY="..."
```
