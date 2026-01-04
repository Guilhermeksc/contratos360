from __future__ import annotations

import logging
import os
import shutil
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple
from zipfile import ZipFile
from xml.etree import ElementTree as ET

import requests
from django.conf import settings
from django.db import transaction
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from ..models import InlabsArticle

logger = logging.getLogger(__name__)

LOGIN_URL = "https://inlabs.in.gov.br/acessar.php"
DEFAULT_SECTION = getattr(settings, "INLABS_SECTION", "DO3")
DEFAULT_KEYWORD = getattr(settings, "INLABS_ARTCATEGORY_KEYWORD", "Comando da Marinha")
DEFAULT_DOWNLOAD_ROOT = Path(
    getattr(settings, "INLABS_DOWNLOAD_ROOT", settings.BASE_DIR / "tmp" / "inlabs")
)
DEFAULT_DOWNLOAD_ROOT.mkdir(parents=True, exist_ok=True)

ARTICLE_FIELD_MAP = {
    "name": "name",
    "idOficio": "id_oficio",
    "pubName": "pub_name",
    "artType": "art_type",
    "pubDate": "pub_date",
    "artClass": "art_class",
    "artCategory": "art_category",
    "artNotes": "art_notes",
    "pdfPage": "pdf_page",
    "editionNumber": "edition_number",
    "highlightType": "highlight_type",
    "highlightPriority": "highlight_priority",
    "highlight": "highlight",
    "highlightimage": "highlight_image",
    "highlightimagename": "highlight_image_name",
    "idMateria": "materia_id",
}


@dataclass
class InlabsDownloadConfig:
    target_date: date
    section: str = DEFAULT_SECTION
    keyword: str = DEFAULT_KEYWORD
    download_root: Path = field(default_factory=lambda: DEFAULT_DOWNLOAD_ROOT)
    max_attempts: int = int(os.getenv("INLABS_DOWNLOAD_ATTEMPTS", "3"))
    wait_timeout: int = int(os.getenv("INLABS_DOWNLOAD_TIMEOUT", "60"))
    retry_delay: int = int(os.getenv("INLABS_DOWNLOAD_RETRY_DELAY", "5"))

    def __post_init__(self) -> None:
        self.download_root.mkdir(parents=True, exist_ok=True)

    @property
    def date_str(self) -> str:
        return self.target_date.strftime("%Y-%m-%d")

    @property
    def download_url(self) -> str:
        return f"https://inlabs.in.gov.br/index.php?p={self.date_str}&dl={self.date_str}-{self.section}.zip"

    @property
    def zip_filename(self) -> str:
        return f"{self.date_str}-{self.section}.zip"

    @property
    def download_dir(self) -> Path:
        path = self.download_root / self.date_str
        path.mkdir(parents=True, exist_ok=True)
        return path


class InlabsDownloadError(RuntimeError):
    """Erro específico para fluxo de download do INLABS."""


def ensure_download_available(url: str, target_date: str) -> None:
    try:
        response = requests.head(url, allow_redirects=True, timeout=20)
    except requests.RequestException as exc:
        raise InlabsDownloadError(
            f"Falha ao verificar disponibilidade da edição {target_date}: {exc}."
        ) from exc

    if response.status_code != 200:
        raise InlabsDownloadError(
            f"Nenhum arquivo disponível para {target_date}. HTTP {response.status_code}."
        )


def get_credentials() -> Tuple[str, str]:
    email = os.getenv("INLABS_EMAIL")
    password = os.getenv("INLABS_PASSWORD")
    if not email or not password:
        raise InlabsDownloadError("Variáveis INLABS_EMAIL e INLABS_PASSWORD não configuradas.")
    return email, password


def build_driver(download_dir: Path) -> webdriver.Chrome:
    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.binary_location = os.getenv("CHROME_BIN", "/usr/bin/chromium")

    prefs = {
        "download.default_directory": str(download_dir),
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
    }
    chrome_opts.add_experimental_option("prefs", prefs)

    driver_path = ChromeDriverManager(chrome_type="chromium").install()
    service = Service(driver_path)
    return webdriver.Chrome(service=service, options=chrome_opts)


def ensure_login_success(wait: WebDriverWait, driver: webdriver.Chrome) -> None:
    try:
        wait.until(lambda d: "acessar.php" not in d.current_url)
    except TimeoutException as exc:
        error_message = ""
        for selector in ("div.alert-danger", "div.alert", "span.error"):
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                error_message = elements[0].text.strip()
                break
        screenshot_path = driver.execute_script("return window.location.href;")
        logger.error(
            "Falha ao autenticar no INLABS. mensagem=%s url=%s", error_message, screenshot_path
        )
        raise InlabsDownloadError(
            "Não foi possível autenticar no INLABS. Verifique credenciais ou CAPTCHA."
        ) from exc


def clean_partial_downloads(directory: Path) -> None:
    removed = False
    for pattern in (".org.chromium.*", "*.crdownload"):
        for temp in directory.glob(pattern):
            try:
                temp.unlink()
                removed = True
            except OSError:
                continue
    if removed:
        logger.info("Artefatos temporários removidos antes de nova tentativa.")


def wait_for_download(directory: Path, final_name: str, timeout: int) -> Path:
    target = directory / final_name
    deadline = time.time() + timeout

    def temp_candidates() -> List[Path]:
        return list(directory.glob(".org.chromium.*")) + list(directory.glob("*.crdownload"))

    logger.info("Aguardando até %ss pelo arquivo %s", timeout, final_name)
    temp_reported = False
    while time.time() < deadline:
        if target.exists():
            logger.info("Arquivo final localizado: %s", target)
            return target
        temps = temp_candidates()
        if temps:
            if not temp_reported:
                names = ", ".join(t.name for t in temps)
                logger.info("Download em andamento (%s)", names)
                temp_reported = True
            time.sleep(1)
            continue
        time.sleep(1)

    temps = temp_candidates()
    if temps and not target.exists():
        temps[0].rename(target)
        logger.warning("Arquivo temporário renomeado para %s", target)
        return target

    raise InlabsDownloadError(
        f"Arquivo {final_name} não apareceu após {timeout} segundos (dir: {directory})."
    )


def perform_download_with_retries(driver: webdriver.Chrome, config: InlabsDownloadConfig) -> Path:
    for attempt in range(1, config.max_attempts + 1):
        logger.info(
            "Iniciando tentativa %s/%s para baixar %s",
            attempt,
            config.max_attempts,
            config.zip_filename,
        )
        clean_partial_downloads(config.download_dir)
        driver.get(config.download_url)
        try:
            return wait_for_download(config.download_dir, config.zip_filename, config.wait_timeout)
        except InlabsDownloadError as exc:
            logger.warning("Tentativa %s falhou: %s", attempt, exc)
            if attempt < config.max_attempts:
                logger.info("Aguardando %ss antes da próxima tentativa", config.retry_delay)
                time.sleep(config.retry_delay)
            else:
                raise
    raise InlabsDownloadError("Falha ao baixar o arquivo após múltiplas tentativas.")


def extract_download(zip_path: Path) -> Path:
    target_dir = zip_path.with_suffix("")
    if target_dir.exists():
        shutil.rmtree(target_dir)
    with ZipFile(zip_path, "r") as archive:
        archive.extractall(target_dir)
    logger.info("Arquivo extraído para %s", target_dir)
    return target_dir


def collect_marinha_articles(root_dir: Path, keyword: str) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    if not root_dir.exists():
        raise InlabsDownloadError(f"Diretório {root_dir} não encontrado para leitura dos XMLs.")

    for xml_file in root_dir.rglob("*.xml"):
        try:
            tree = ET.parse(xml_file)
        except ET.ParseError:
            logger.warning("XML inválido ignorado: %s", xml_file)
            continue

        article = tree.getroot()
        if article.tag != "article":
            article = article.find("article")
            if article is None:
                continue

        art_category = article.attrib.get("artCategory", "")
        if keyword.lower() not in art_category.lower():
            continue

        body_elem = article.find("body")
        body_html = ET.tostring(body_elem, encoding="unicode") if body_elem is not None else ""

        results.append(
            {
                "attributes": dict(article.attrib),
                "body_html": body_html,
                "source_filename": xml_file.name,
            }
        )

    logger.info("%s artigos encontrados com o termo '%s'", len(results), keyword)
    return results


def fetch_inlabs_articles(config: InlabsDownloadConfig) -> Tuple[Path, List[Dict[str, object]]]:
    ensure_download_available(config.download_url, config.date_str)
    email, password = get_credentials()
    driver = build_driver(config.download_dir)
    zip_path: Path

    try:
        wait = WebDriverWait(driver, 20)
        driver.get(LOGIN_URL)
        login_form = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form[action='logar.php']"))
        )
        email_input = login_form.find_element(By.CSS_SELECTOR, "input[name='email']")
        password_input = login_form.find_element(By.CSS_SELECTOR, "input[name='password']")
        submit_btn = login_form.find_element(By.CSS_SELECTOR, "input[type='submit']")

        email_input.send_keys(email)
        password_input.send_keys(password)
        submit_btn.click()

        ensure_login_success(wait, driver)
        zip_path = perform_download_with_retries(driver, config)
    finally:
        driver.quit()

    extracted_dir = extract_download(zip_path)
    articles = collect_marinha_articles(extracted_dir, config.keyword)
    return zip_path, articles


def persist_inlabs_articles(
    edition_date: date, articles: List[Dict[str, object]], source_zip: str | None = None
) -> int:
    saved = 0

    with transaction.atomic():
        for article in articles:
            attrs: Dict[str, str] = article.get("attributes", {})
            article_id = attrs.get("id")
            if not article_id:
                continue

            defaults: Dict[str, object] = {
                "edition_date": edition_date,
                "body_html": article.get("body_html", ""),
                "source_filename": article.get("source_filename", ""),
                "source_zip": source_zip or "",
                "raw_payload": attrs,
            }

            for xml_key, model_field in ARTICLE_FIELD_MAP.items():
                defaults[model_field] = attrs.get(xml_key, "")

            obj, created = InlabsArticle.objects.update_or_create(
                article_id=article_id,
                edition_date=edition_date,
                defaults=defaults,
            )
            saved += 1
            action = "criado" if created else "atualizado"
            logger.debug("Artigo %s %s", obj.article_id, action)

    logger.info("%s artigos persistidos para %s", saved, edition_date)
    return saved


def ingest_inlabs_articles(target_date: date | None = None) -> Dict[str, object]:
    target = target_date or date.today()
    config = InlabsDownloadConfig(target_date=target)
    zip_path, articles = fetch_inlabs_articles(config)
    saved = persist_inlabs_articles(target, articles, source_zip=zip_path.name)
    return {
        "edition_date": target.isoformat(),
        "downloaded_file": str(zip_path),
        "saved_articles": saved,
    }