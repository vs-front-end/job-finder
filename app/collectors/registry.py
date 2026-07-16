from __future__ import annotations

import os

from app.collectors.ats import AtsCollector
from app.collectors.base import Collector
from app.collectors.feeds import (
    ArbeitnowCollector,
    HimalayasCollector,
    JobicyCollector,
    LandingJobsCollector,
    RemoteFirstJobsCollector,
    RemoteJobsOrgCollector,
    RemoteOkCollector,
    RemotiveCollector,
    RssCollector,
    StartupJobsCollector,
    TheMuseCollector,
    WeWorkRemotelyCollector,
    WorkingNomadsCollector,
)
from app.collectors.hacker_news import HackerNewsCollector
from app.collectors.public_pages import ArcCollector, GetOnBoardCollector, YCombinatorCollector
from app.config import AppConfig


def build_collectors(config: AppConfig) -> list[Collector]:
    timeout = config.limites.timeout_segundos
    limit = config.limites.itens_por_fonte
    collectors: list[Collector] = []
    enabled = config.fontes
    if enabled.himalayas:
        collectors.append(HimalayasCollector(timeout, limit, config.buscas.termos))
    if enabled.jobicy:
        collectors.append(JobicyCollector(timeout, limit))
    if enabled.remote_ok:
        collectors.append(RemoteOkCollector(timeout, limit))
    if enabled.remotive:
        collectors.append(RemotiveCollector(timeout, limit))
    if enabled.we_work_remotely:
        collectors.append(WeWorkRemotelyCollector(timeout, limit))
    if enabled.arbeitnow:
        collectors.append(ArbeitnowCollector(timeout, limit))
    if enabled.hacker_news:
        collectors.append(HackerNewsCollector(timeout, limit))
    if enabled.arc:
        collectors.append(
            ArcCollector(
                timeout,
                limit,
                config.filtros.idade_maxima_dias,
                config.buscas.arc_tags,
            )
        )
    if enabled.y_combinator:
        collectors.append(YCombinatorCollector(timeout, limit, config.filtros.idade_maxima_dias))
    the_muse_key = os.getenv("THE_MUSE_API_KEY")
    if enabled.the_muse and the_muse_key:
        collectors.append(TheMuseCollector(timeout, limit, the_muse_key))
    if enabled.get_on_board:
        collectors.append(GetOnBoardCollector(timeout, limit, config.filtros.idade_maxima_dias))
    startup_jobs_key = os.getenv("STARTUP_JOBS_API_KEY")
    if enabled.startup_jobs and startup_jobs_key:
        collectors.append(StartupJobsCollector(timeout, limit, startup_jobs_key))
    if enabled.working_nomads:
        collectors.append(WorkingNomadsCollector(timeout, limit))
    if enabled.remotejobs_org:
        collectors.append(RemoteJobsOrgCollector(timeout, limit))
    if enabled.landing_jobs:
        collectors.append(LandingJobsCollector(timeout, limit))
    if enabled.jobspresso:
        collectors.append(
            RssCollector("jobspresso", "https://jobspresso.co/?feed=job_feed", timeout, limit)
        )
    if enabled.remote_first_jobs:
        collectors.append(RemoteFirstJobsCollector(timeout, limit))
    for index, url in enumerate(config.feeds.google_alerts):
        collectors.append(RssCollector(f"google_alert_{index + 1}", url, timeout, limit))
    for index, url in enumerate(config.feeds.extras):
        collectors.append(RssCollector(f"extra_feed_{index + 1}", url, timeout, limit))
    if enabled.ats:
        collectors.extend(
            AtsCollector(company, timeout, limit) for company in config.empresas if company.ativo
        )
    return collectors
