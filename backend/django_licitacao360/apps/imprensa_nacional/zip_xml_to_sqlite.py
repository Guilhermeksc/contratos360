from __future__ import annotations

import argparse
import html
import re
import sqlite3
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

DOWNLOADS_DIR = Path(__file__).resolve().parent / "downloads"
DEFAULT_DB = Path(__file__).resolve().parent / "inlabs_articles.sqlite3"
ZIP_PATTERN = re.compile(r"^S03\d{2}\d{4}\.zip$")
DEFAULT_KEYWORD = "Comando da Marinha"
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


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS inlabs_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id TEXT,
            name TEXT,
            id_oficio TEXT,
            pub_name TEXT,
            art_type TEXT,
            pub_date TEXT,
            nome_om TEXT,
            number_page TEXT,
            pdf_page TEXT,
            edition_number TEXT,
            highlight_type TEXT,
            highlight_priority TEXT,
            highlight TEXT,
            highlight_image TEXT,
            highlight_image_name TEXT,
            materia_id TEXT,
            body_identifica TEXT,
            uasg TEXT,
            body_texto TEXT,
            UNIQUE(article_id, pub_date, materia_id)
        );

        CREATE TABLE IF NOT EXISTS aviso_licitacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id TEXT UNIQUE,
            modalidade TEXT,
            numero TEXT,
            ano TEXT,
            uasg TEXT,
            processo TEXT,
            objeto TEXT,
            itens_licitados TEXT,
            publicacao TEXT,
            entrega_propostas TEXT,
            abertura_propostas TEXT,
            nome_responsavel TEXT,
            cargo TEXT
        );

        CREATE TABLE IF NOT EXISTS credenciamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id TEXT UNIQUE,
            tipo TEXT,
            numero TEXT,
            ano TEXT,
            uasg TEXT,
            processo TEXT,
            tipo_processo TEXT,
            numero_processo TEXT,
            ano_processo TEXT,
            contratante TEXT,
            contratado TEXT,
            objeto TEXT,
            fundamento_legal TEXT,
            vigencia TEXT,
            valor_total TEXT,
            data_assinatura TEXT,
            nome_responsavel TEXT,
            cargo TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_pub_date ON inlabs_articles(pub_date);
        CREATE INDEX IF NOT EXISTS idx_article_id ON inlabs_articles(article_id);
        CREATE INDEX IF NOT EXISTS idx_materia_id ON inlabs_articles(materia_id);
        """
    )

    try:
        conn.execute("ALTER TABLE inlabs_articles ADD COLUMN uasg TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE inlabs_articles ADD COLUMN nome_om TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE aviso_licitacao DROP COLUMN endereco")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE aviso_licitacao DROP COLUMN informacoes_gerais")
    except sqlite3.OperationalError:
        pass


def parse_article(xml_bytes: bytes) -> dict[str, str | None]:
    root = ET.fromstring(xml_bytes)
    article = root.find("article") if root.tag != "article" else root
    if article is None:
        raise ValueError("XML sem nó <article>.")

    attrs = article.attrib
    body = article.find("body")

    def body_text(tag: str) -> str | None:
        if body is None:
            return None
        elem = body.find(tag)
        return elem.text if elem is not None else None

    body_identifica = body_text("Identifica")
    uasg_match = UASG_PATTERN.search(body_identifica or "")
    uasg = uasg_match.group(1) if uasg_match else None

    art_category = attrs.get("artCategory")
    nome_om = art_category.rsplit("/", 1)[-1].strip() if art_category else None

    return {
        "article_id": attrs.get("id"),
        "name": attrs.get("name"),
        "id_oficio": attrs.get("idOficio"),
        "pub_name": attrs.get("pubName"),
        "art_type": attrs.get("artType"),
        "pub_date": attrs.get("pubDate"),
        "art_class": attrs.get("artClass"),
        "art_category": art_category,
        "nome_om": nome_om,
        "art_size": attrs.get("artSize"),
        "art_notes": attrs.get("artNotes"),
        "number_page": attrs.get("numberPage"),
        "pdf_page": attrs.get("pdfPage"),
        "edition_number": attrs.get("editionNumber"),
        "highlight_type": attrs.get("highlightType"),
        "highlight_priority": attrs.get("highlightPriority"),
        "highlight": attrs.get("highlight"),
        "highlight_image": attrs.get("highlightimage"),
        "highlight_image_name": attrs.get("highlightimagename"),
        "materia_id": attrs.get("idMateria"),
        "body_identifica": body_identifica,
        "uasg": uasg,
        "body_texto": body_text("Texto"),
        "raw_xml": xml_bytes.decode("utf-8", errors="ignore"),
    }


def extract_paragraphs(body_html: str | None) -> list[tuple[str | None, str]]:
    if not body_html:
        return []
    paragraphs = re.findall(r"<p(?:\s+class=\"([^\"]*)\")?>(.*?)</p>", body_html, re.DOTALL | re.IGNORECASE)
    results: list[tuple[str | None, str]] = []
    for class_name, content in paragraphs:
        text = re.sub(r"<[^>]+>", "", content)
        text = html.unescape(text).strip()
        results.append((class_name, text))
    return results


def extract_labeled_fields(text: str) -> dict[str, str]:
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
    results: dict[str, str] = {}
    for idx, match in enumerate(matches):
        label = match.group(1)
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        value = text[start:end].strip()
        results[label] = value
    return results


def parse_aviso_licitacao(body_html: str | None) -> dict[str, str | None]:
    data: dict[str, str | None] = {
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
    info_texts: list[str] = []
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
        data.pop("informacoes_gerais", None)

    return data


def parse_credenciamento(body_html: str | None) -> dict[str, str | None]:
    data: dict[str, str | None] = {
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


def insert_article(cursor: sqlite3.Cursor, data: dict[str, str | None]) -> None:
    cursor.execute(
        """
        INSERT OR IGNORE INTO inlabs_articles (
            article_id, name, id_oficio, pub_name, art_type, pub_date,
            nome_om, number_page, pdf_page, edition_number,
            highlight_type, highlight_priority, highlight, highlight_image,
            highlight_image_name, materia_id, body_identifica, uasg, body_texto
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("article_id"),
            data.get("name"),
            data.get("id_oficio"),
            data.get("pub_name"),
            data.get("art_type"),
            data.get("pub_date"),
            data.get("nome_om"),
            data.get("number_page"),
            data.get("pdf_page"),
            data.get("edition_number"),
            data.get("highlight_type"),
            data.get("highlight_priority"),
            data.get("highlight"),
            data.get("highlight_image"),
            data.get("highlight_image_name"),
            data.get("materia_id"),
            data.get("body_identifica"),
            data.get("uasg"),
            data.get("body_texto"),
        ),
    )


def insert_aviso(cursor: sqlite3.Cursor, article_id: str, aviso: dict[str, str | None]) -> None:
    cursor.execute(
        """
        INSERT OR REPLACE INTO aviso_licitacao (
            article_id, modalidade, numero, ano, uasg, processo, objeto,
            itens_licitados, publicacao, entrega_propostas,
            abertura_propostas, nome_responsavel, cargo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            article_id,
            aviso.get("modalidade"),
            aviso.get("numero"),
            aviso.get("ano"),
            aviso.get("uasg"),
            aviso.get("processo"),
            aviso.get("objeto"),
            aviso.get("itens_licitados"),
            aviso.get("publicacao"),
            aviso.get("entrega_propostas"),
            aviso.get("abertura_propostas"),
            aviso.get("nome_responsavel"),
            aviso.get("cargo"),
        ),
    )


def insert_credenciamento(
    cursor: sqlite3.Cursor, article_id: str, cred: dict[str, str | None]
) -> None:
    cursor.execute(
        """
        INSERT OR REPLACE INTO credenciamento (
            article_id, tipo, numero, ano, uasg, processo, tipo_processo,
            numero_processo, ano_processo, contratante, contratado, objeto,
            fundamento_legal, vigencia, valor_total, data_assinatura,
            nome_responsavel, cargo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            article_id,
            cred.get("tipo"),
            cred.get("numero"),
            cred.get("ano"),
            cred.get("uasg"),
            cred.get("processo"),
            cred.get("tipo_processo"),
            cred.get("numero_processo"),
            cred.get("ano_processo"),
            cred.get("contratante"),
            cred.get("contratado"),
            cred.get("objeto"),
            cred.get("fundamento_legal"),
            cred.get("vigencia"),
            cred.get("valor_total"),
            cred.get("data_assinatura"),
            cred.get("nome_responsavel"),
            cred.get("cargo"),
        ),
    )


def iter_zip_files(only_zip: str | None) -> list[Path]:
    if only_zip:
        path = DOWNLOADS_DIR / only_zip
        if not path.exists():
            raise FileNotFoundError(f"Zip não encontrado: {path}")
        return [path]

    return sorted(
        [
            p
            for p in DOWNLOADS_DIR.iterdir()
            if p.is_file() and ZIP_PATTERN.match(p.name)
        ]
    )


def process_zip(conn: sqlite3.Connection, zip_path: Path, keyword: str) -> None:
    cursor = conn.cursor()
    inserted = 0
    skipped = 0

    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            if not name.lower().endswith(".xml"):
                continue
            try:
                xml_bytes = zf.read(name)
                data = parse_article(xml_bytes)
                art_category = (data.get("art_category") or "").lower()
                if keyword.lower() not in art_category:
                    skipped += 1
                    continue
                art_type = data.get("art_type")
                aviso = None
                cred = None
                if art_type in AVISO_ART_TYPES:
                    aviso = parse_aviso_licitacao(data.get("body_texto"))
                    if not data.get("uasg") and aviso.get("uasg"):
                        data["uasg"] = aviso.get("uasg")

                if art_type and "credenciamento" in art_type.lower():
                    cred = parse_credenciamento(data.get("body_texto"))
                    if not data.get("uasg") and cred.get("uasg"):
                        data["uasg"] = cred.get("uasg")

                insert_article(cursor, data)

                if aviso is not None:
                    article_id = data.get("article_id")
                    if article_id:
                        insert_aviso(cursor, article_id, aviso)
                if cred is not None:
                    article_id = data.get("article_id")
                    if article_id:
                        insert_credenciamento(cursor, article_id, cred)
                inserted += 1
            except Exception:
                skipped += 1

    conn.commit()
    print(f"{zip_path.name}: inseridos={inserted} ignorados={skipped}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extrai XMLs dos zips e grava em SQLite."
    )
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DB),
        help="Caminho do SQLite (padrão: inlabs_articles.sqlite3).",
    )
    parser.add_argument(
        "--only",
        dest="only_zip",
        default="S03012025.zip",
        help="Processa apenas este zip (padrão: S03012025.zip).",
    )
    parser.add_argument(
        "--keyword",
        default=DEFAULT_KEYWORD,
        help="Filtro em artCategory (padrão: 'Comando da Marinha').",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Processa todos os zips S03{MM}{YYYY}.zip na pasta downloads.",
    )

    args = parser.parse_args()

    db_path = Path(args.db)
    conn = sqlite3.connect(str(db_path))
    create_schema(conn)

    if args.all:
        zip_files = iter_zip_files(None)
    else:
        zip_files = iter_zip_files(args.only_zip)

    if not zip_files:
        print("Nenhum zip encontrado para processar.")
        return

    for zip_path in zip_files:
        process_zip(conn, zip_path, args.keyword)

    conn.close()


if __name__ == "__main__":
    main()
