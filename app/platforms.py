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
            "Public API with search, country, timezone and date filters.",
        ),
        _active(
            "jobicy",
            "Jobicy",
            "https://jobicy.com/",
            "Global",
            "Public remote jobs API with location and salary data.",
        ),
        _active(
            "remote_ok",
            "Remote OK",
            "https://remoteok.com/",
            "Global",
            "Public API with a local post-filter for remote development roles.",
        ),
        _active(
            "remotive",
            "Remotive",
            "https://remotive.com/",
            "Global",
            "Public API filtered to software development.",
        ),
        _active(
            "we_work_remotely",
            "We Work Remotely",
            "https://weworkremotely.com/",
            "Global",
            "Programming-specific RSS feeds.",
        ),
        _active(
            "arbeitnow",
            "Arbeitnow",
            "https://www.arbeitnow.com/",
            "Global",
            "Public API with a remote filter.",
        ),
        _active(
            "hacker_news",
            "Hacker News Who Is Hiring",
            "https://news.ycombinator.com/jobs",
            "Community",
            "Monthly thread collected through the HN Algolia API.",
        ),
        _active(
            "arc",
            "Arc.dev",
            "https://arc.dev/remote-jobs",
            "Global",
            "Structured public pages by technology.",
        ),
        _active(
            "y_combinator",
            "Y Combinator Jobs",
            "https://www.ycombinator.com/jobs",
            "Startups",
            "Remote engineering roles at YC startups.",
        ),
        PlatformDefinition(
            "the_muse",
            "The Muse",
            "https://www.themuse.com/search/jobs",
            "Global",
            the_muse_availability,
            "Public API filtered to remote software engineering.",
        ),
        _active(
            "get_on_board",
            "Get on Board",
            "https://www.getonbrd.com/jobs/programming",
            "LATAM",
            "Public pages with date, allowed region and salary.",
        ),
        PlatformDefinition(
            "startup_jobs",
            "Startup Jobs",
            "https://startup.jobs/",
            "Startups",
            startup_availability,
            "Official API for remote engineering roles; requires a free key.",
        ),
        _active(
            "working_nomads",
            "Working Nomads",
            "https://www.workingnomads.com/jobs",
            "Global",
            "Public API with the latest jobs filtered to development.",
        ),
        _active(
            "remotejobs_org",
            "RemoteJobs.org",
            "https://remotejobs.org/",
            "Global",
            "Free public API filtered to the programming category.",
        ),
        _active(
            "landing_jobs",
            "Landing.jobs",
            "https://landing.jobs/",
            "Europe",
            "Public API for remote jobs with allowed countries and salary.",
        ),
        _active(
            "jobspresso",
            "Jobspresso",
            "https://jobspresso.co/",
            "Global",
            "Public RSS feed of curated remote jobs.",
        ),
        _active(
            "remote_first_jobs",
            "RemoteFirstJobs",
            "https://remotefirstjobs.com/",
            "Global",
            "React and software development RSS feeds updated every 10 minutes.",
        ),
        _active(
            "greenhouse",
            "Greenhouse",
            "https://www.greenhouse.com/",
            "ATS",
            "Public boards of the configured companies.",
        ),
        _active(
            "lever", "Lever", "https://www.lever.co/", "ATS", "Public Postings API per company."
        ),
        _active(
            "ashby",
            "Ashby",
            "https://www.ashbyhq.com/",
            "ATS",
            "Public Job Postings API per company.",
        ),
        _manual(
            "wellfound",
            "Wellfound",
            "https://wellfound.com/jobs",
            "Startups",
            "Startup search and profile; public automation is blocked.",
        ),
        _manual(
            "welcome_jungle",
            "Welcome to the Jungle / Otta",
            "https://app.welcometothejungle.com/jobs",
            "Startups",
            "Personalized search available after login.",
        ),
        _manual(
            "linkedin",
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/",
            "Global",
            "Create alerts with remote, your region and last-week filters.",
        ),
        _manual(
            "indeed",
            "Indeed",
            "https://www.indeed.com/",
            "Global",
            "Manual search; scraping integrations stay out of scope.",
        ),
        _manual(
            "glassdoor",
            "Glassdoor",
            "https://www.glassdoor.com/Job/index.htm",
            "Global",
            "Manual search because the terms forbid unauthorized scraping.",
        ),
        _manual(
            "google_jobs",
            "Google Jobs / Alerts",
            "https://www.google.com/search?q=remote+software+engineer+jobs",
            "Search",
            "Use x-ray queries and alerts; there is no public job search API.",
        ),
        _manual(
            "toptal",
            "Toptal",
            "https://www.toptal.com/talent/apply",
            "Talent network",
            "Create and maintain a specialized freelancer profile.",
        ),
        _manual(
            "turing",
            "Turing",
            "https://www.turing.com/jobs",
            "Talent network",
            "Private matching after assessment and profile.",
        ),
        _manual(
            "crossover",
            "Crossover",
            "https://www.crossover.com/jobs",
            "Global",
            "Public catalog without a documented search API.",
        ),
        _manual(
            "terminal",
            "Terminal",
            "https://www.terminal.io/engineers",
            "Talent network",
            "Engineer matching by profile and country.",
        ),
        _manual(
            "vanhack",
            "VanHack",
            "https://vanhack.com/",
            "LATAM",
            "International opportunities tied to your profile.",
        ),
        _manual(
            "remote_com",
            "Remote.com Jobs",
            "https://remote.com/jobs",
            "Global",
            "Search and profile; Remote's public API is an HR API.",
        ),
        _manual(
            "braintrust",
            "Braintrust",
            "https://www.usebraintrust.com/",
            "Talent network",
            "Private marketplace for freelancers and contracts.",
        ),
        _manual(
            "lemon",
            "Lemon.io",
            "https://lemon.io/for-developers/",
            "Talent network",
            "Private matching for experienced developers.",
        ),
        _manual(
            "gun",
            "Gun.io",
            "https://gun.io/jobs/",
            "Talent network",
            "Public list without reliable dates per opportunity.",
        ),
        _manual(
            "revelo",
            "Revelo",
            "https://careers.revelo.com/",
            "LATAM",
            "Network focused on LATAM talent and US companies.",
        ),
        _manual(
            "tecla",
            "Tecla",
            "https://www.tecla.io/join",
            "LATAM",
            "Network of LATAM developers for US companies.",
        ),
        _manual(
            "howdy",
            "Howdy",
            "https://www.howdy.com/",
            "LATAM",
            "Talent network and opportunities for Latin America.",
        ),
        _manual(
            "andela",
            "Andela",
            "https://www.andela.com/talent",
            "Talent network",
            "Global marketplace of technical professionals.",
        ),
        _manual(
            "torre",
            "Torre",
            "https://torre.ai/",
            "LATAM",
            "Profile and matching for remote opportunities.",
        ),
        _manual(
            "coodesh",
            "Coodesh",
            "https://coodesh.com/vagas",
            "Brazil",
            "Tech profile and jobs in Brazil and abroad.",
        ),
        _manual(
            "latojobs",
            "LATOjobs",
            "https://latojobs.com/",
            "LATAM",
            "Regional remote job board.",
        ),
        _manual(
            "weremoto",
            "WeRemoto",
            "https://www.weremoto.com/",
            "LATAM",
            "Remote board for Latin American professionals.",
        ),
        _manual(
            "lupa_roles",
            "Lupa Roles",
            "https://www.lupahire.com/",
            "LATAM",
            "Opportunities and matching for LATAM talent.",
        ),
        _manual(
            "geekhunter",
            "GeekHunter",
            "https://www.geekhunter.com.br/",
            "Brazil",
            "Tech profile and matching with companies.",
        ),
        _manual(
            "programathor",
            "ProgramaThor",
            "https://programathor.com.br/jobs",
            "Brazil",
            "Brazilian board focused on development.",
        ),
        _manual(
            "remotar",
            "Remotar",
            "https://remotar.com.br/",
            "Brazil",
            "Brazilian curation of remote work.",
        ),
        _manual(
            "github_lists",
            "GitHub lists",
            "https://github.com/remoteintech/remote-jobs",
            "Seeds",
            "Public lists used to discover companies and their ATS.",
        ),
        _planned(
            "smartrecruiters",
            "SmartRecruiters",
            "https://www.smartrecruiters.com/",
            "ATS",
            "Public Posting API per company.",
        ),
        _planned(
            "workable",
            "Workable",
            "https://www.workable.com/",
            "ATS",
            "Public careers endpoints per subdomain.",
        ),
        _planned(
            "recruitee",
            "Recruitee",
            "https://recruitee.com/",
            "ATS",
            "Public Careers Site API per company.",
        ),
        _planned(
            "personio",
            "Personio",
            "https://www.personio.com/",
            "ATS",
            "XML feed when enabled by the company.",
        ),
        _planned(
            "workday",
            "Workday",
            "https://www.workday.com/",
            "ATS",
            "Public pages without a stable API; experimental integration.",
        ),
        _planned(
            "gupy",
            "Gupy",
            "https://portal.gupy.io/",
            "ATS Brazil",
            "Public portal and job pages; experimental integration.",
        ),
        _planned(
            "teamtailor",
            "Teamtailor and other ATS",
            "https://www.teamtailor.com/",
            "ATS",
            "JSON-LD, feeds or public pages depending on the company.",
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
