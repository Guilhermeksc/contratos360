import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from datetime import date
from dotenv import load_dotenv
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


""" 
docker compose exec backend bash
cd django_licitacao360/apps/imprensa_nacional/scripts
python inlabs.py

docker compose exec backend python manage.py import_inlabs --date 2026-01-02
"""

LOGIN_URL = "https://inlabs.in.gov.br/acessar.php"
SECTION = "DO3"
SCRIPT_DIR = Path(__file__).resolve().parent


def build_download_url(date_str: str, section: str = SECTION) -> str:
    return f"https://inlabs.in.gov.br/index.php?p={date_str}&dl={date_str}-{section}.zip"


TODAY_STR = date.today().strftime("%Y-%m-%d")
TARGET_DATE = os.environ.get("INLABS_TARGET_DATE", TODAY_STR)
DOWNLOAD_URL = build_download_url(TARGET_DATE)

ARTICLE_FIELDS = [
    "id",
    "name",
    "idOficio",
    "pubName",
    "artType",
    "pubDate",
    "artClass",
    "artCategory",
    "artNotes",
    "pdfPage",
    "editionNumber",
    "highlightType",
    "highlightPriority",
    "highlight",
    "highlightimage",
    "highlightimagename",
    "idMateria",
]

MAX_DOWNLOAD_ATTEMPTS = int(os.environ.get("INLABS_DOWNLOAD_ATTEMPTS", "3"))
DOWNLOAD_WAIT_TIMEOUT = int(os.environ.get("INLABS_DOWNLOAD_TIMEOUT", "60"))
DOWNLOAD_RETRY_DELAY = int(os.environ.get("INLABS_DOWNLOAD_RETRY_DELAY", "5"))


def _extract_filename(download_url: str) -> str:
    parsed = urlparse(download_url)
    file_from_query = parse_qs(parsed.query).get("dl", [])
    if file_from_query:
        return file_from_query[0]
    return Path(parsed.path).name or "download.zip"


DOWNLOAD_FILENAME = _extract_filename(DOWNLOAD_URL)
DOWNLOAD_DIR = SCRIPT_DIR
OUTPUT_JSON = SCRIPT_DIR / f"inlabs_comando_marinha_{TARGET_DATE}.json"


def ensure_download_available(url: str, target_date: str) -> None:
    try:
        response = requests.head(url, allow_redirects=True, timeout=20)
        if response.status_code == 200:
            return
        print(
            f"Nenhum arquivo disponível para {target_date}. Resposta HTTP: {response.status_code}."
        )
    except requests.RequestException as exc:
        print(
            f"Falha ao verificar a edição {target_date}: {exc}. Tente novamente ou informe INLABS_TARGET_DATE."
        )
    sys.exit(0)


ensure_download_available(DOWNLOAD_URL, TARGET_DATE)

def load_env_file(filename: str = ".env") -> bool:
    """Procura por um arquivo .env na hierarquia e carrega o primeiro encontrado."""
    current = SCRIPT_DIR
    for directory in [current] + list(current.parents):
        env_path = directory / filename
        if env_path.exists():
            load_dotenv(env_path)
            return True
    return False


load_env_file()

email = os.environ.get("INLABS_EMAIL")
password = os.environ.get("INLABS_PASSWORD")
if not email or not password:
    raise RuntimeError("Credenciais não definidas nas variáveis de ambiente.")

chrome_opts = Options()
chrome_opts.add_argument("--headless=new")
chrome_opts.add_argument("--disable-gpu")
chrome_opts.add_argument("--no-sandbox")
chrome_opts.binary_location = os.getenv("CHROME_BIN", "/usr/bin/chromium")
chrome_opts.add_argument("--disable-dev-shm-usage")

prefs = {
    "download.default_directory": str(DOWNLOAD_DIR),
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True,
}
chrome_opts.add_experimental_option("prefs", prefs)

driver_path = ChromeDriverManager(chrome_type="chromium").install()
driver = webdriver.Chrome(service=Service(driver_path), options=chrome_opts)


def ensure_login_success(wait: WebDriverWait, driver: webdriver.Chrome) -> None:
    """Confirma que o login saiu da tela de credenciais ou levanta um erro detalhado."""
    try:
        wait.until(lambda d: "acessar.php" not in d.current_url)
        return
    except TimeoutException as exc:
        error_message = ""
        for selector in ("div.alert-danger", "div.alert", "span.error"):
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                error_message = elements[0].text.strip()
                break
        screenshot_path = Path.cwd() / "login_error.png"
        driver.save_screenshot(str(screenshot_path))
        raise RuntimeError(
            "Login não confirmou. Verifique credenciais, CAPTCHA e a captura login_error.png."
            + (f" Mensagem na página: {error_message}" if error_message else "")
        ) from exc


def wait_for_download(directory: Path, final_name: str, timeout: int) -> Path:
    """Aguarda o Chromium finalizar o download e retorna o caminho do arquivo."""
    target = directory / final_name
    deadline = time.time() + timeout

    def temp_candidates() -> list[Path]:
        return list(directory.glob(".org.chromium.*")) + list(directory.glob("*.crdownload"))

    print(f"Aguardando até {timeout}s pelo arquivo final {final_name}...")
    temp_reported = False
    while time.time() < deadline:
        if target.exists():
            print(f"Arquivo final localizado: {target}")
            return target
        temps = temp_candidates()
        if temps:
            if not temp_reported:
                names = ", ".join(t.name for t in temps)
                print(f"Arquivos temporários detectados ({names}). Download em andamento...")
                temp_reported = True
            time.sleep(1)
            continue
        time.sleep(1)

    temps = temp_candidates()
    if temps and not target.exists():
        temps[0].rename(target)
        print(f"Arquivo temporário renomeado para {target}")
        return target

    raise RuntimeError(
        f"Arquivo {final_name} não apareceu após {timeout} segundos (dir: {directory})."
    )


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
        print("Arquivos temporários antigos removidos antes da nova tentativa.")


def extract_download(zip_path: Path) -> Path:
    target_dir = zip_path.with_suffix("")
    with ZipFile(zip_path, "r") as archive:
        archive.extractall(target_dir)
    return target_dir


def collect_marinha_articles(root_dir: Path, keyword: str = "Comando da Marinha") -> list[dict]:
    results: list[dict] = []
    if not root_dir.exists():
        raise RuntimeError(f"Diretório {root_dir} não encontrado para o processamento dos XMLs.")

    for xml_file in root_dir.rglob("*.xml"):
        try:
            tree = ET.parse(xml_file)
        except ET.ParseError:
            continue

        article = tree.getroot()
        if article.tag != "article":
            article = article.find("article")
            if article is None:
                continue

        if keyword not in article.attrib.get("artCategory", ""):
            continue

        body_elem = article.find("body")
        body_html = ET.tostring(body_elem, encoding="unicode") if body_elem is not None else ""

        record = {field: article.attrib.get(field, "") for field in ARTICLE_FIELDS}
        record["body_html"] = body_html
        results.append(record)

    return results


def persist_results(records: list[dict], destination: Path) -> None:
    with destination.open("w", encoding="utf-8") as fp:
        json.dump(records, fp, ensure_ascii=False, indent=2)


def perform_download_with_retries(driver: webdriver.Chrome) -> Path:
    for attempt in range(1, MAX_DOWNLOAD_ATTEMPTS + 1):
        print(
            f"Iniciando tentativa {attempt}/{MAX_DOWNLOAD_ATTEMPTS} para baixar {DOWNLOAD_FILENAME} ({TARGET_DATE})."
        )
        clean_partial_downloads(DOWNLOAD_DIR)
        driver.get(DOWNLOAD_URL)
        try:
            return wait_for_download(
                DOWNLOAD_DIR,
                DOWNLOAD_FILENAME,
                timeout=DOWNLOAD_WAIT_TIMEOUT,
            )
        except RuntimeError as exc:
            print(f"Tentativa {attempt} falhou: {exc}")
            if attempt < MAX_DOWNLOAD_ATTEMPTS:
                print(f"Aguardando {DOWNLOAD_RETRY_DELAY}s antes de tentar novamente...")
                time.sleep(DOWNLOAD_RETRY_DELAY)
            else:
                raise

try:
    wait = WebDriverWait(driver, 20)
    driver.get(LOGIN_URL)

    # Seletores específicos do formulário de login (form[action="logar.php"])
    login_form = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form[action='logar.php']")))
    email_input = login_form.find_element(By.CSS_SELECTOR, "input[name='email']")
    password_input = login_form.find_element(By.CSS_SELECTOR, "input[name='password']")
    submit_btn = login_form.find_element(By.CSS_SELECTOR, "input[type='submit']")

    email_input.send_keys(email)
    password_input.send_keys(password)
    submit_btn.click()

    ensure_login_success(wait, driver)

    # Download
    downloaded = perform_download_with_retries(driver)
    print(f"Download concluído em {downloaded}")

    extracted_dir = extract_download(downloaded)
    articles = collect_marinha_articles(extracted_dir)
    persist_results(articles, OUTPUT_JSON)
    print(f"{len(articles)} registros encontrados e salvos em {OUTPUT_JSON}")
finally:
    driver.quit()
