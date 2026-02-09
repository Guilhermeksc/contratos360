from __future__ import annotations

import html
import logging
import os
import re
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

from ..models import InlabsArticle, AvisoLicitacao, Credenciamento

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
    "numberPage": "number_page",
    "pdfPage": "pdf_page",
    "editionNumber": "edition_number",
    "highlightType": "highlight_type",
    "highlightPriority": "highlight_priority",
    "highlight": "highlight",
    "highlightimage": "highlight_image",
    "highlightimagename": "highlight_image_name",
    "idMateria": "materia_id",
}

# Padrões regex para parsing (compatíveis com zip_xml_to_sqlite.py)
UASG_PATTERN = re.compile(r"\bUASG\s*(\d+)\b", re.IGNORECASE)
AVISO_ART_TYPES = {"Aviso de Licitação-Pregão", "Aviso de Licitação", "Aviso de Licitação-Concorrência"}
AVISO_IDENT_PATTERN = re.compile(
    r"^(?P<modalidade>.+?)\s+N[ºo]\s*(?P<numero>\d+)/(?:\s*)?(?P<ano>\d{4})\s*-\s*UASG\s*(?P<uasg>\d+)",
    re.IGNORECASE,
)
CRED_IDENT_PATTERN = re.compile(
    r"^(?P<tipo>.+?)\s+N[ºo]\s*(?P<numero>\d+)/(?:\s*)?(?P<ano>\d{4})\s*-\s*UASG\s*(?P<uasg>\d+)",
    re.IGNORECASE,
)
CRED_PROCES_PATTERN = re.compile(
    r"^Nº Processo:\s*(?P<processo>.+)$",
    re.IGNORECASE,
)
CRED_CONTRATANTE_PATTERN = re.compile(
    r"^(?P<tipo_processo>[^.]+?)\s+N[ºo]\s*(?P<numero_processo>\d+)/(?:\s*)?(?P<ano_processo>\d{4})\.\s*Contratante:\s*(?P<contratante>.+?)\.$",
    re.IGNORECASE,
)
CRED_CONTRATADO_PATTERN = re.compile(
    r"^Contratado:\s*(?P<contratado>.+?)\.\s*Objeto:\s*(?P<objeto>.+?)\.$",
    re.IGNORECASE,
)
CRED_FUNDAMENTO_PATTERN = re.compile(
    r"^Fundamento Legal:\s*(?P<fundamento_legal>.+?)\.\s*Vigência:\s*(?P<vigencia>.+?)\.\s*Valor Total:\s*(?P<valor_total>.+?)\.\s*Data de Assinatura:\s*(?P<data_assinatura>.+?)\.$",
    re.IGNORECASE,
)
CRED_ASSINA_PATTERN = re.compile(r"^(?P<nome>.+?)\s*\((?P<cargo>[^)]+)\)$")


@dataclass
class InlabsDownloadConfig:
    target_date: date
    section: str = DEFAULT_SECTION
    keyword: str = DEFAULT_KEYWORD
    download_root: Path = field(default_factory=lambda: DEFAULT_DOWNLOAD_ROOT)
    max_attempts: int = int(os.getenv("INLABS_DOWNLOAD_ATTEMPTS", "2"))
    wait_timeout: int = int(os.getenv("INLABS_DOWNLOAD_TIMEOUT", "10"))  #  10 segundos
    retry_delay: int = int(os.getenv("INLABS_DOWNLOAD_RETRY_DELAY", "4"))

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


def extract_paragraphs(body_html: str | None) -> List[Tuple[str | None, str]]:
    """Extrai parágrafos do HTML com suas classes."""
    if not body_html:
        return []
    paragraphs = re.findall(r"<p(?:\s+class=\"([^\"]*)\")?>(.*?)</p>", body_html, re.DOTALL | re.IGNORECASE)
    results: List[Tuple[str | None, str]] = []
    for class_name, content in paragraphs:
        text = re.sub(r"<[^>]+>", "", content)
        text = html.unescape(text).strip()
        results.append((class_name, text))
    return results


def extract_labeled_fields(text: str) -> Dict[str, str]:
    """Extrai campos rotulados do texto."""
    labels = [
        "Nº Processo",
        "Objeto",
        "Total de Itens Licitados",
        "Edital",
        "Endereço",
        "Entrega das Propostas",
        "Abertura das Propostas",
        "Informações Gerais",
    ]
    pattern = re.compile(
        r"(Nº Processo|Objeto|Total de Itens Licitados|Edital|Endereço|Entrega das Propostas|Abertura das Propostas|Informações Gerais):",
        re.IGNORECASE,
    )
    matches = list(pattern.finditer(text))
    results: Dict[str, str] = {}
    for idx, match in enumerate(matches):
        label = match.group(1)
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        value = text[start:end].strip()
        results[label] = value
    return results


def parse_aviso_licitacao(body_html: str | None) -> Dict[str, str | None]:
    """Extrai dados de aviso de licitação do HTML."""
    data: Dict[str, str | None] = {
        "modalidade": None,
        "numero": None,
        "ano": None,
        "uasg": None,
        "processo": None,
        "objeto": None,
        "itens_licitados": None,
        "publicacao": None,
        "entrega_propostas": None,
        "abertura_propostas": None,
        "nome_responsavel": None,
        "cargo": None,
    }

    paragraphs = extract_paragraphs(body_html)
    if not paragraphs:
        return data

    identifica_text = None
    info_texts: List[str] = []
    for class_name, text in paragraphs:
        class_name_lower = (class_name or "").lower()
        if class_name_lower == "identifica":
            if AVISO_IDENT_PATTERN.search(text):
                identifica_text = text
        elif class_name_lower == "assina":
            data["nome_responsavel"] = text
        elif class_name_lower == "cargo":
            data["cargo"] = text
        else:
            if "siasgnet" not in text.lower():
                info_texts.append(text)

    if identifica_text:
        match = AVISO_IDENT_PATTERN.search(identifica_text)
        if match:
            data.update(match.groupdict())

    if info_texts:
        joined = " ".join(info_texts)
        fields = extract_labeled_fields(joined)
        data["processo"] = fields.get("Nº Processo")
        data["objeto"] = fields.get("Objeto")
        itens_raw = fields.get("Total de Itens Licitados")
        if itens_raw:
            data["itens_licitados"] = itens_raw.rstrip(".")
        publicacao_raw = fields.get("Edital")
        if publicacao_raw:
            data["publicacao"] = publicacao_raw.split()[0]

        entrega_raw = fields.get("Entrega das Propostas")
        if entrega_raw:
            match = re.search(r"\d{2}/\d{2}/\d{4}", entrega_raw)
            data["entrega_propostas"] = match.group(0) if match else None
        abertura_raw = fields.get("Abertura das Propostas")
        if abertura_raw:
            match = re.search(
                r"\d{2}/\d{2}/\d{4}\s+às\s+\d{2}h\d{2}\s+no\s+site\s+www\.gov\.br/compras\.?",
                abertura_raw,
                re.IGNORECASE,
            )
            if match:
                data["abertura_propostas"] = match.group(0)
            else:
                match = re.search(r"\d{2}/\d{2}/\d{4}", abertura_raw)
                data["abertura_propostas"] = match.group(0) if match else None

    return data


def parse_credenciamento(body_html: str | None) -> Dict[str, str | None]:
    """Extrai dados de credenciamento do HTML."""
    data: Dict[str, str | None] = {
        "tipo": None,
        "numero": None,
        "ano": None,
        "uasg": None,
        "processo": None,
        "tipo_processo": None,
        "numero_processo": None,
        "ano_processo": None,
        "contratante": None,
        "contratado": None,
        "objeto": None,
        "fundamento_legal": None,
        "vigencia": None,
        "valor_total": None,
        "data_assinatura": None,
        "nome_responsavel": None,
        "cargo": None,
    }

    paragraphs = extract_paragraphs(body_html)
    if not paragraphs:
        return data

    identifica_text = None
    for class_name, text in paragraphs:
        class_name_lower = (class_name or "").lower()
        if class_name_lower == "identifica":
            if CRED_IDENT_PATTERN.search(text):
                identifica_text = text
        elif class_name_lower == "assina":
            data["nome_responsavel"] = text
        elif class_name_lower == "cargo":
            data["cargo"] = text
        else:
            if "comprasnet" in text.lower():
                continue

            match = CRED_PROCES_PATTERN.match(text)
            if match:
                data["processo"] = match.group("processo").strip().rstrip(".")
                continue

            match = CRED_CONTRATANTE_PATTERN.match(text)
            if match:
                data.update(match.groupdict())
                continue

            match = CRED_CONTRATADO_PATTERN.match(text)
            if match:
                data.update(match.groupdict())
                continue

            match = CRED_FUNDAMENTO_PATTERN.match(text)
            if match:
                data.update(match.groupdict())
                continue

            match = CRED_ASSINA_PATTERN.match(text)
            if match:
                data["nome_responsavel"] = match.group("nome")
                data["cargo"] = match.group("cargo")

    if identifica_text:
        match = CRED_IDENT_PATTERN.search(identifica_text)
        if match:
            data.update(match.groupdict())

    return data


def collect_marinha_articles(root_dir: Path, keyword: str) -> List[Dict[str, object]]:
    """Coleta artigos do INLABS relacionados ao Comando da Marinha."""
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

        # Extrai body_identifica e body_texto (compatível com zip_xml_to_sqlite.py)
        body_identifica = None
        body_texto = None
        if body_elem is not None:
            identifica_elem = body_elem.find("Identifica")
            if identifica_elem is not None:
                body_identifica = identifica_elem.text or ""
            
            texto_elem = body_elem.find("Texto")
            if texto_elem is not None:
                # O elemento <Texto> pode conter HTML de duas formas:
                # 1. Como texto escapado dentro do elemento (texto_elem.text) - ex: &lt;p&gt;texto&lt;/p&gt;
                # 2. Como elementos XML filhos (tags <p> como elementos XML) - ex: <p>texto</p>
                
                # Tenta primeiro pegar elementos filhos (se existirem)
                if len(texto_elem) > 0:
                    # Tem elementos filhos XML - converte para HTML
                    texto_parts = []
                    if texto_elem.text:
                        # Desescapa o texto do elemento raiz
                        texto_parts.append(html.unescape(texto_elem.text))
                    for child in texto_elem:
                        # Converte o elemento filho para HTML string
                        child_html = ET.tostring(child, encoding="unicode", method="html")
                        # Desescapa o HTML resultante (pode conter entidades escapadas no texto)
                        child_html = html.unescape(child_html)
                        texto_parts.append(child_html)
                        if child.tail:
                            # Desescapa o tail também
                            texto_parts.append(html.unescape(child.tail))
                    texto_html = "".join(texto_parts)
                    body_texto = texto_html if texto_html else None
                else:
                    # Não tem elementos filhos - pega o texto direto (que contém HTML escapado)
                    texto_html = texto_elem.text or ""
                    # Decodifica entidades HTML (&lt; -> <, &gt; -> >, &amp; -> &, etc.)
                    body_texto = html.unescape(texto_html) if texto_html else None

        # Extrai nome_om do art_category
        nome_om = None
        if art_category:
            nome_om = art_category.rsplit("/", 1)[-1].strip()

        # Extrai UASG do body_identifica
        uasg = None
        if body_identifica:
            uasg_match = UASG_PATTERN.search(body_identifica)
            if uasg_match:
                uasg = uasg_match.group(1)

        results.append(
            {
                "attributes": dict(article.attrib),
                "body_html": body_html,
                "body_identifica": body_identifica,
                "body_texto": body_texto,
                "nome_om": nome_om,
                "uasg": uasg,
                "source_filename": xml_file.name,
            }
        )

    logger.info("%s artigos encontrados com o termo '%s'", len(results), keyword)
    
    # Log de tipos encontrados para debug
    art_types_summary = {}
    for article_data in results:
        art_type = article_data.get("attributes", {}).get("artType", "")
        if art_type:
            art_types_summary[art_type] = art_types_summary.get(art_type, 0) + 1
    
    if art_types_summary:
        logger.info("Tipos de artigos encontrados:")
        for art_type, count in sorted(art_types_summary.items()):
            logger.info("  - %s: %s", art_type, count)
        logger.info("Tipos esperados para avisos: %s", AVISO_ART_TYPES)
    
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


def normalize_pub_date(date_str: str) -> str:
    """
    Normaliza uma data para o formato YYYY-MM-DD.
    Aceita formatos: DD/MM/YYYY, YYYY-MM-DD, ou outros formatos comuns.
    """
    if not date_str or not isinstance(date_str, str):
        raise ValueError(f"Data inválida: {date_str}")
    
    date_str = date_str.strip()
    
    # Se já está no formato YYYY-MM-DD, retorna como está
    if len(date_str) == 10 and date_str.count('-') == 2:
        try:
            from datetime import datetime
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            pass
    
    # Tenta formato DD/MM/YYYY
    if len(date_str) == 10 and date_str.count('/') == 2:
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            pass
    
    # Tenta outros formatos comuns
    from datetime import datetime
    formats = [
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%Y.%m.%d",
        "%d.%m.%Y",
    ]
    
    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # Se não conseguir converter, tenta usar a data como está (pode ser inválida)
    logger.warning(f"Não foi possível normalizar a data: {date_str}, usando como está")
    return date_str


def persist_inlabs_articles(
    edition_date: date, articles: List[Dict[str, object]], source_zip: str | None = None
) -> Dict[str, int]:
    """Persiste artigos INLABS e cria registros relacionados em AvisoLicitacao e Credenciamento.
    
    Returns:
        Dict com contadores: saved_articles, saved_avisos, saved_credenciamentos
    """
    saved = 0
    avisos_saved = 0
    credenciamentos_saved = 0
    
    # Estatísticas para debug
    art_types_found = {}
    avisos_processed = 0
    avisos_skipped = 0
    credenciamentos_processed = 0
    credenciamentos_skipped = 0

    try:
        with transaction.atomic():
            for article_data in articles:
                attrs: Dict[str, str] = article_data.get("attributes", {})
                article_id = attrs.get("id")
                if not article_id:
                    logger.warning("Artigo sem ID ignorado: %s", article_data.get("source_filename", "desconhecido"))
                    continue

                # Prepara dados para InlabsArticle (compatível com zip_xml_to_sqlite.py)
                # Normaliza pub_date para formato YYYY-MM-DD
                pub_date_raw = attrs.get("pubDate", edition_date.strftime("%Y-%m-%d"))
                pub_date = normalize_pub_date(pub_date_raw) if pub_date_raw else edition_date.strftime("%Y-%m-%d")
                materia_id = attrs.get("idMateria", "")

                defaults: Dict[str, object] = {
                    "name": attrs.get("name", ""),
                    "id_oficio": attrs.get("idOficio", ""),
                    "pub_name": attrs.get("pubName", ""),
                    "art_type": attrs.get("artType", ""),
                    "pub_date": pub_date,
                    "nome_om": article_data.get("nome_om"),
                    "number_page": attrs.get("numberPage", ""),
                    "pdf_page": attrs.get("pdfPage", ""),
                    "edition_number": attrs.get("editionNumber", ""),
                    "highlight_type": attrs.get("highlightType", ""),
                    "highlight_priority": attrs.get("highlightPriority", ""),
                    "highlight": attrs.get("highlight", ""),
                    "highlight_image": attrs.get("highlightimage", ""),
                    "highlight_image_name": attrs.get("highlightimagename", ""),
                    "materia_id": materia_id,
                    "body_identifica": article_data.get("body_identifica"),
                    "uasg": article_data.get("uasg"),
                    "body_texto": article_data.get("body_texto"),
                }

                # Cria ou atualiza o artigo
                obj, created = InlabsArticle.objects.update_or_create(
                    article_id=article_id,
                    pub_date=pub_date,
                    materia_id=materia_id,
                    defaults=defaults,
                )
                saved += 1
                action = "criado" if created else "atualizado"
                logger.debug("Artigo %s %s", obj.article_id, action)

                # Coleta estatísticas de art_types
                art_type = attrs.get("artType", "")
                if art_type:
                    art_types_found[art_type] = art_types_found.get(art_type, 0) + 1

                # Processa aviso de licitação se aplicável
                # Usa body_texto para parsing (contém HTML decodificado de <Texto>)
                # body_html contém a estrutura XML completa com HTML escapado dentro de <Texto>
                body_html_for_parsing = article_data.get("body_texto") or article_data.get("body_html")
                
                if art_type in AVISO_ART_TYPES:
                    avisos_processed += 1
                    logger.info("🔍 AVISO DETECTADO: article_id=%s, art_type=%s", article_id, art_type)
                    logger.info("   body_html presente: %s (tamanho: %s)", 
                               bool(article_data.get("body_html")), 
                               len(article_data.get("body_html", "")))
                    logger.info("   body_texto presente: %s (tamanho: %s)", 
                               bool(article_data.get("body_texto")), 
                               len(article_data.get("body_texto", "")))
                    logger.info("   body_html_for_parsing tamanho: %s", 
                               len(body_html_for_parsing) if body_html_for_parsing else 0)
                    
                    # Mostra amostra do HTML para debug (primeiros 500 caracteres)
                    if body_html_for_parsing:
                        sample = body_html_for_parsing[:500].replace('\n', ' ').replace('\r', '')
                        logger.info("   Amostra HTML DECODIFICADO (500 chars): %s...", sample)
                        # Verifica se tem tags <p> no HTML
                        has_p_tags = '<p' in body_html_for_parsing.lower()
                        logger.info("   Contém tags <p>: %s", has_p_tags)
                    
                    aviso_data = parse_aviso_licitacao(body_html_for_parsing)
                    logger.info("   Resultado do parsing: modalidade=%s, numero=%s, ano=%s, uasg=%s, processo=%s",
                               aviso_data.get("modalidade"), aviso_data.get("numero"), 
                               aviso_data.get("ano"), aviso_data.get("uasg"), aviso_data.get("processo"))
                    
                    # Atualiza UASG do artigo se não estava presente
                    if not obj.uasg and aviso_data.get("uasg"):
                        obj.uasg = aviso_data.get("uasg")
                        obj.save(update_fields=["uasg"])

                    # Salva ou atualiza aviso de licitação
                    # Verifica se há dados suficientes para salvar (modalidade OU numero OU processo)
                    has_modalidade = bool(aviso_data.get("modalidade"))
                    has_numero = bool(aviso_data.get("numero"))
                    has_processo = bool(aviso_data.get("processo"))
                    
                    logger.info("   Condições: modalidade=%s, numero=%s, processo=%s", 
                               has_modalidade, has_numero, has_processo)
                    
                    if has_modalidade or has_numero or has_processo:
                        AvisoLicitacao.objects.update_or_create(
                            article_id=article_id,
                            defaults={
                                "modalidade": aviso_data.get("modalidade"),
                                "numero": aviso_data.get("numero"),
                                "ano": aviso_data.get("ano"),
                                "uasg": aviso_data.get("uasg"),
                                "processo": aviso_data.get("processo"),
                                "objeto": aviso_data.get("objeto"),
                                "itens_licitados": aviso_data.get("itens_licitados"),
                                "publicacao": aviso_data.get("publicacao"),
                                "entrega_propostas": aviso_data.get("entrega_propostas"),
                                "abertura_propostas": aviso_data.get("abertura_propostas"),
                                "nome_responsavel": aviso_data.get("nome_responsavel"),
                                "cargo": aviso_data.get("cargo"),
                            }
                        )
                        avisos_saved += 1
                        logger.info("   ✅ Aviso de licitação %s SALVO", article_id)
                    else:
                        avisos_skipped += 1
                        logger.warning("   ⚠️  Aviso de licitação %s IGNORADO (sem dados suficientes: modalidade=%s, numero=%s, processo=%s)", 
                                     article_id, has_modalidade, has_numero, has_processo)

                # Processa credenciamento se aplicável
                if art_type and "credenciamento" in art_type.lower():
                    credenciamentos_processed += 1
                    logger.info("🔍 CREDENCIAMENTO DETECTADO: article_id=%s, art_type=%s", article_id, art_type)
                    logger.info("   body_html presente: %s (tamanho: %s)", 
                               bool(article_data.get("body_html")), 
                               len(article_data.get("body_html", "")))
                    logger.info("   body_texto presente: %s (tamanho: %s)", 
                               bool(article_data.get("body_texto")), 
                               len(article_data.get("body_texto", "")))
                    logger.info("   body_html_for_parsing tamanho: %s", 
                               len(body_html_for_parsing) if body_html_for_parsing else 0)
                    
                    # Mostra amostra do HTML para debug (primeiros 500 caracteres)
                    if body_html_for_parsing:
                        sample = body_html_for_parsing[:500].replace('\n', ' ').replace('\r', '')
                        logger.info("   Amostra HTML DECODIFICADO (500 chars): %s...", sample)
                        # Verifica se tem tags <p> no HTML
                        has_p_tags = '<p' in body_html_for_parsing.lower()
                        logger.info("   Contém tags <p>: %s", has_p_tags)
                    
                    cred_data = parse_credenciamento(body_html_for_parsing)
                    logger.info("   Resultado do parsing: tipo=%s, numero=%s, ano=%s, uasg=%s, processo=%s",
                               cred_data.get("tipo"), cred_data.get("numero"), 
                               cred_data.get("ano"), cred_data.get("uasg"), cred_data.get("processo"))
                    # Atualiza UASG do artigo se não estava presente
                    if not obj.uasg and cred_data.get("uasg"):
                        obj.uasg = cred_data.get("uasg")
                        obj.save(update_fields=["uasg"])

                    # Salva ou atualiza credenciamento
                    # Verifica se há dados suficientes para salvar (tipo OU numero OU processo)
                    has_tipo = bool(cred_data.get("tipo"))
                    has_numero_cred = bool(cred_data.get("numero"))
                    has_processo_cred = bool(cred_data.get("processo"))
                    
                    logger.info("   Condições: tipo=%s, numero=%s, processo=%s", 
                               has_tipo, has_numero_cred, has_processo_cred)
                    
                    if has_tipo or has_numero_cred or has_processo_cred:
                        Credenciamento.objects.update_or_create(
                            article_id=article_id,
                            defaults={
                                "tipo": cred_data.get("tipo"),
                                "numero": cred_data.get("numero"),
                                "ano": cred_data.get("ano"),
                                "uasg": cred_data.get("uasg"),
                                "processo": cred_data.get("processo"),
                                "tipo_processo": cred_data.get("tipo_processo"),
                                "numero_processo": cred_data.get("numero_processo"),
                                "ano_processo": cred_data.get("ano_processo"),
                                "contratante": cred_data.get("contratante"),
                                "contratado": cred_data.get("contratado"),
                                "objeto": cred_data.get("objeto"),
                                "fundamento_legal": cred_data.get("fundamento_legal"),
                                "vigencia": cred_data.get("vigencia"),
                                "valor_total": cred_data.get("valor_total"),
                                "data_assinatura": cred_data.get("data_assinatura"),
                                "nome_responsavel": cred_data.get("nome_responsavel"),
                                "cargo": cred_data.get("cargo"),
                            }
                        )
                        credenciamentos_saved += 1
                        logger.info("   ✅ Credenciamento %s SALVO", article_id)
                    else:
                        credenciamentos_skipped += 1
                        logger.warning("   ⚠️  Credenciamento %s IGNORADO (sem dados suficientes: tipo=%s, numero=%s, processo=%s)", 
                                     article_id, has_tipo, has_numero_cred, has_processo_cred)
            
    except Exception as exc:
        logger.error("Erro ao persistir artigos INLABS para %s: %s", edition_date, exc, exc_info=True)
        raise

    # Log de estatísticas detalhadas
    logger.info("=" * 80)
    logger.info("ESTATÍSTICAS DE IMPORTAÇÃO - %s", edition_date)
    logger.info("=" * 80)
    logger.info("Total de artigos: %s", saved)
    logger.info("Tipos de artigos encontrados:")
    for art_type, count in sorted(art_types_found.items()):
        logger.info("  - %s: %s", art_type, count)
    logger.info("")
    logger.info("Avisos de Licitação:")
    logger.info("  - Processados: %s", avisos_processed)
    logger.info("  - Salvos: %s", avisos_saved)
    logger.info("  - Ignorados: %s", avisos_skipped)
    logger.info("")
    logger.info("Credenciamentos:")
    logger.info("  - Processados: %s", credenciamentos_processed)
    logger.info("  - Salvos: %s", credenciamentos_saved)
    logger.info("  - Ignorados: %s", credenciamentos_skipped)
    logger.info("=" * 80)
    
    logger.info(
        "%s artigos persistidos para %s (avisos: %s, credenciamentos: %s)",
        saved,
        edition_date,
        avisos_saved,
        credenciamentos_saved,
    )
    return {
        "saved_articles": saved,
        "saved_avisos": avisos_saved,
        "saved_credenciamentos": credenciamentos_saved,
    }


def ingest_inlabs_articles(target_date: date | None = None) -> Dict[str, object]:
    """Função principal que orquestra o download e persistência de artigos INLABS."""
    target = target_date or date.today()
    config = InlabsDownloadConfig(target_date=target)
    zip_path, articles = fetch_inlabs_articles(config)
    stats = persist_inlabs_articles(target, articles, source_zip=zip_path.name)
    return {
        "edition_date": target.isoformat(),
        "downloaded_file": str(zip_path),
        "saved_articles": stats["saved_articles"],
        "saved_avisos": stats["saved_avisos"],
        "saved_credenciamentos": stats["saved_credenciamentos"],
    }