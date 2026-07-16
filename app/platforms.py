from __future__ import annotations

import os
from dataclasses import dataclass

from app.models import PlatformAvailability


@dataclass(frozen=True)
class PlatformDefinition:
    id: str
    name: str
    url: str
    category: str
    availability: PlatformAvailability
    description: str


def platform_catalog() -> tuple[PlatformDefinition, ...]:
    the_muse_availability = (
        PlatformAvailability.ACTIVE
        if os.getenv("THE_MUSE_API_KEY")
        else PlatformAvailability.NEEDS_KEY
    )
    startup_availability = (
        PlatformAvailability.ACTIVE
        if os.getenv("STARTUP_JOBS_API_KEY")
        else PlatformAvailability.NEEDS_KEY
    )
    return (
        _active(
            "himalayas",
            "Himalayas",
            "https://himalayas.app/jobs",
            "Global",
            "API pública com filtros de busca, país, fuso e data.",
        ),
        _active(
            "jobicy",
            "Jobicy",
            "https://jobicy.com/",
            "Global",
            "API pública de vagas remotas com localização e salário.",
        ),
        _active(
            "remote_ok",
            "Remote OK",
            "https://remoteok.com/",
            "Global",
            "API pública e pós-filtro local para desenvolvimento remoto.",
        ),
        _active(
            "remotive",
            "Remotive",
            "https://remotive.com/",
            "Global",
            "API pública filtrada para software development.",
        ),
        _active(
            "we_work_remotely",
            "We Work Remotely",
            "https://weworkremotely.com/",
            "Global",
            "Feeds RSS específicos de programação.",
        ),
        _active(
            "arbeitnow",
            "Arbeitnow",
            "https://www.arbeitnow.com/",
            "Global",
            "API pública com filtro remoto.",
        ),
        _active(
            "hacker_news",
            "Hacker News Who Is Hiring",
            "https://news.ycombinator.com/jobs",
            "Comunidade",
            "Thread mensal coletada pela API do HN Algolia.",
        ),
        _active(
            "arc",
            "Arc.dev",
            "https://arc.dev/remote-jobs",
            "Global",
            "Páginas públicas estruturadas por tecnologia.",
        ),
        _active(
            "y_combinator",
            "Y Combinator Jobs",
            "https://www.ycombinator.com/jobs",
            "Startups",
            "Vagas remotas de engenharia em startups do YC.",
        ),
        PlatformDefinition(
            "the_muse",
            "The Muse",
            "https://www.themuse.com/search/jobs",
            "Global",
            the_muse_availability,
            "API pública filtrada para software engineering e remoto.",
        ),
        _active(
            "get_on_board",
            "Get on Board",
            "https://www.getonbrd.com/jobs/programming",
            "LATAM",
            "Páginas públicas com data, região permitida e salário.",
        ),
        PlatformDefinition(
            "startup_jobs",
            "Startup Jobs",
            "https://startup.jobs/",
            "Startups",
            startup_availability,
            "API oficial de vagas remotas de engenharia; requer chave gratuita.",
        ),
        _active(
            "working_nomads",
            "Working Nomads",
            "https://www.workingnomads.com/jobs",
            "Global",
            "API pública com as vagas mais recentes filtradas por desenvolvimento.",
        ),
        _active(
            "remotejobs_org",
            "RemoteJobs.org",
            "https://remotejobs.org/",
            "Global",
            "API pública gratuita filtrada pela categoria programming.",
        ),
        _active(
            "landing_jobs",
            "Landing.jobs",
            "https://landing.jobs/",
            "Europa",
            "API pública de vagas remotas com países permitidos e salário.",
        ),
        _active(
            "jobspresso",
            "Jobspresso",
            "https://jobspresso.co/",
            "Global",
            "Feed RSS público de vagas remotas curadas.",
        ),
        _active(
            "remote_first_jobs",
            "RemoteFirstJobs",
            "https://remotefirstjobs.com/",
            "Global",
            "Feeds RSS de React e software development atualizados a cada 10 minutos.",
        ),
        _active(
            "greenhouse",
            "Greenhouse",
            "https://www.greenhouse.com/",
            "ATS",
            "Boards públicos das empresas configuradas.",
        ),
        _active(
            "lever", "Lever", "https://www.lever.co/", "ATS", "Postings API pública por empresa."
        ),
        _active(
            "ashby",
            "Ashby",
            "https://www.ashbyhq.com/",
            "ATS",
            "Public Job Postings API por empresa.",
        ),
        _manual(
            "wellfound",
            "Wellfound",
            "https://wellfound.com/jobs",
            "Startups",
            "Busca e perfil de startups; automação pública é bloqueada.",
        ),
        _manual(
            "welcome_jungle",
            "Welcome to the Jungle / Otta",
            "https://app.welcometothejungle.com/jobs",
            "Startups",
            "Busca personalizada disponível após login.",
        ),
        _manual(
            "linkedin",
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Global",
            "Criar alertas com remoto, Brasil/LATAM e data da última semana.",
        ),
        _manual(
            "indeed",
            "Indeed",
            "https://www.indeed.com/",
            "Global",
            "Pesquisa manual; integração por scraping permanece opcional.",
        ),
        _manual(
            "glassdoor",
            "Glassdoor",
            "https://www.glassdoor.com/Job/index.htm",
            "Global",
            "Pesquisa manual porque os termos proíbem scraping sem autorização.",
        ),
        _manual(
            "google_jobs",
            "Google Jobs / Alerts",
            "https://www.google.com/search?q=remote+software+engineer+LATAM+jobs",
            "Busca",
            "Usar consultas x-ray e alertas; não existe API de busca de vagas.",
        ),
        _manual(
            "toptal",
            "Toptal",
            "https://www.toptal.com/talent/apply",
            "Rede de talentos",
            "Criar e manter perfil de freelancer especializado.",
        ),
        _manual(
            "turing",
            "Turing",
            "https://www.turing.com/jobs",
            "Rede de talentos",
            "Matching privado após avaliação e perfil.",
        ),
        _manual(
            "crossover",
            "Crossover",
            "https://www.crossover.com/jobs",
            "Global",
            "Catálogo público sem API de busca documentada.",
        ),
        _manual(
            "terminal",
            "Terminal",
            "https://www.terminal.io/engineers",
            "Rede de talentos",
            "Matching de engenheiros por perfil e país.",
        ),
        _manual(
            "vanhack",
            "VanHack",
            "https://vanhack.com/",
            "LATAM",
            "Oportunidades internacionais vinculadas ao perfil.",
        ),
        _manual(
            "remote_com",
            "Remote.com Jobs",
            "https://remote.com/jobs",
            "Global",
            "Pesquisa e perfil; a API pública da Remote é de RH.",
        ),
        _manual(
            "braintrust",
            "Braintrust",
            "https://www.usebraintrust.com/",
            "Rede de talentos",
            "Marketplace privado de freelancers e contratos.",
        ),
        _manual(
            "lemon",
            "Lemon.io",
            "https://lemon.io/for-developers/",
            "Rede de talentos",
            "Matching privado para desenvolvedores experientes.",
        ),
        _manual(
            "gun",
            "Gun.io",
            "https://gun.io/jobs/",
            "Rede de talentos",
            "Lista pública sem data confiável por oportunidade.",
        ),
        _manual(
            "revelo",
            "Revelo",
            "https://careers.revelo.com/",
            "LATAM",
            "Rede voltada a talentos LATAM e empresas dos EUA.",
        ),
        _manual(
            "tecla",
            "Tecla",
            "https://www.tecla.io/join",
            "LATAM",
            "Rede de desenvolvedores LATAM para empresas dos EUA.",
        ),
        _manual(
            "howdy",
            "Howdy",
            "https://www.howdy.com/",
            "LATAM",
            "Rede de talentos e oportunidades para a América Latina.",
        ),
        _manual(
            "andela",
            "Andela",
            "https://www.andela.com/talent",
            "Rede de talentos",
            "Marketplace global de profissionais técnicos.",
        ),
        _manual(
            "torre",
            "Torre",
            "https://torre.ai/",
            "LATAM",
            "Perfil e matching de oportunidades remotas.",
        ),
        _manual(
            "coodesh",
            "Coodesh",
            "https://coodesh.com/vagas",
            "Brasil",
            "Perfil e vagas de tecnologia no Brasil e exterior.",
        ),
        _manual(
            "latojobs",
            "LATOjobs",
            "https://latojobs.com/",
            "LATAM",
            "Board regional de vagas remotas.",
        ),
        _manual(
            "weremoto",
            "WeRemoto",
            "https://www.weremoto.com/",
            "LATAM",
            "Board remoto para profissionais da América Latina.",
        ),
        _manual(
            "lupa_roles",
            "Lupa Roles",
            "https://www.lupahire.com/",
            "LATAM",
            "Oportunidades e matching para talentos LATAM.",
        ),
        _manual(
            "geekhunter",
            "GeekHunter",
            "https://www.geekhunter.com.br/",
            "Brasil",
            "Perfil de tecnologia e matching com empresas.",
        ),
        _manual(
            "programathor",
            "ProgramaThor",
            "https://programathor.com.br/jobs",
            "Brasil",
            "Board brasileiro focado em desenvolvimento.",
        ),
        _manual(
            "remotar",
            "Remotar",
            "https://remotar.com.br/",
            "Brasil",
            "Curadoria brasileira de trabalho remoto.",
        ),
        _manual(
            "github_lists",
            "Listas no GitHub",
            "https://github.com/remoteintech/remote-jobs",
            "Sementes",
            "Listas públicas usadas para descobrir empresas e seus ATS.",
        ),
        _planned(
            "smartrecruiters",
            "SmartRecruiters",
            "https://www.smartrecruiters.com/",
            "ATS",
            "Posting API pública por empresa.",
        ),
        _planned(
            "workable",
            "Workable",
            "https://www.workable.com/",
            "ATS",
            "Endpoints públicos de carreiras por subdomínio.",
        ),
        _planned(
            "recruitee",
            "Recruitee",
            "https://recruitee.com/",
            "ATS",
            "Careers Site API pública por empresa.",
        ),
        _planned(
            "personio",
            "Personio",
            "https://www.personio.com/",
            "ATS",
            "Feed XML quando habilitado pela empresa.",
        ),
        _planned(
            "workday",
            "Workday",
            "https://www.workday.com/",
            "ATS",
            "Páginas públicas sem API estável; integração experimental.",
        ),
        _planned(
            "gupy",
            "Gupy",
            "https://portal.gupy.io/",
            "ATS Brasil",
            "Portal público e páginas de vagas; integração experimental.",
        ),
        _planned(
            "teamtailor",
            "Teamtailor e outros ATS",
            "https://www.teamtailor.com/",
            "ATS",
            "JSON-LD, feeds ou páginas públicas conforme a empresa.",
        ),
    )


def _active(
    id_value: str, name: str, url: str, category: str, description: str
) -> PlatformDefinition:
    return PlatformDefinition(
        id_value, name, url, category, PlatformAvailability.ACTIVE, description
    )


def _manual(
    id_value: str, name: str, url: str, category: str, description: str
) -> PlatformDefinition:
    return PlatformDefinition(
        id_value, name, url, category, PlatformAvailability.MANUAL, description
    )


def _planned(
    id_value: str, name: str, url: str, category: str, description: str
) -> PlatformDefinition:
    return PlatformDefinition(
        id_value, name, url, category, PlatformAvailability.PLANNED, description
    )
