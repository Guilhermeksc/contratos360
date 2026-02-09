from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from ...models import InlabsArticle


class Command(BaseCommand):
    help = "Exporta todos os dados do modelo InlabsArticle para um arquivo SQLite."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            dest="output_file",
            default="inlabs_articles.db",
            help="Caminho do arquivo SQLite de saída (padrão: inlabs_articles.db).",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Sobrescreve o arquivo SQLite se ele já existir.",
        )

    def handle(self, *args, **options):
        output_file = Path(options["output_file"])
        
        # Verificar se o arquivo já existe
        if output_file.exists() and not options.get("overwrite", False):
            raise CommandError(
                f"Arquivo '{output_file}' já existe. Use --overwrite para sobrescrever."
            )

        # Criar conexão SQLite
        try:
            conn = sqlite3.connect(str(output_file))
            cursor = conn.cursor()
        except Exception as exc:
            raise CommandError(f"Erro ao criar arquivo SQLite: {exc}") from exc

        try:
            # Criar tabela baseada no modelo
            self.stdout.write("Criando estrutura da tabela...")
            self._create_table(cursor)

            # Buscar todos os artigos
            self.stdout.write("Buscando artigos do banco de dados...")
            articles = InlabsArticle.objects.all()
            total_count = articles.count()
            
            if total_count == 0:
                self.stdout.write(self.style.WARNING("Nenhum artigo encontrado no banco de dados."))
                conn.close()
                return

            self.stdout.write(f"Encontrados {total_count} artigos. Exportando...")

            # Inserir dados em lotes
            batch_size = 1000
            inserted_count = 0

            for i in range(0, total_count, batch_size):
                batch = articles[i:i + batch_size]
                self._insert_batch(cursor, batch)
                inserted_count += len(batch)
                
                if inserted_count % 1000 == 0:
                    self.stdout.write(f"  Exportados {inserted_count}/{total_count} artigos...")

            # Commit e criar índices
            self.stdout.write("Criando índices...")
            self._create_indexes(cursor)
            
            conn.commit()
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ Exportação concluída com sucesso!\n"
                    f"   Arquivo: {output_file.absolute()}\n"
                    f"   Total de artigos exportados: {inserted_count}"
                )
            )

        except Exception as exc:
            conn.rollback()
            raise CommandError(f"Erro durante a exportação: {exc}") from exc
        finally:
            conn.close()

    def _create_table(self, cursor):
        """Cria a tabela no SQLite baseada no modelo InlabsArticle."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS imprensa_nacional_inlabsarticle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id VARCHAR(64) NOT NULL,
                edition_date DATE NOT NULL,
                name VARCHAR(255),
                id_oficio VARCHAR(100),
                pub_name VARCHAR(100),
                art_type VARCHAR(100),
                pub_date VARCHAR(32),
                art_class VARCHAR(255),
                art_category VARCHAR(255),
                art_notes TEXT,
                pdf_page VARCHAR(255),
                edition_number VARCHAR(32),
                highlight_type VARCHAR(64),
                highlight_priority VARCHAR(64),
                highlight TEXT,
                highlight_image VARCHAR(255),
                highlight_image_name VARCHAR(255),
                materia_id VARCHAR(64),
                body_html TEXT,
                source_filename VARCHAR(255),
                source_zip VARCHAR(255),
                raw_payload TEXT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                UNIQUE(article_id, edition_date)
            )
        """)

    def _insert_batch(self, cursor, articles):
        """Insere um lote de artigos no SQLite."""
        insert_sql = """
            INSERT INTO imprensa_nacional_inlabsarticle (
                article_id, edition_date, name, id_oficio, pub_name, art_type,
                pub_date, art_class, art_category, art_notes, pdf_page,
                edition_number, highlight_type, highlight_priority, highlight,
                highlight_image, highlight_image_name, materia_id, body_html,
                source_filename, source_zip, raw_payload, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        values = []
        for article in articles:
            # Serializar raw_payload (JSONField) para string JSON
            raw_payload_str = json.dumps(article.raw_payload, ensure_ascii=False) if article.raw_payload else "{}"
            
            values.append((
                article.article_id,
                article.edition_date.isoformat() if article.edition_date else None,
                article.name or None,
                article.id_oficio or None,
                article.pub_name or None,
                article.art_type or None,
                article.pub_date or None,
                article.art_class or None,
                article.art_category or None,
                article.art_notes or None,
                article.pdf_page or None,
                article.edition_number or None,
                article.highlight_type or None,
                article.highlight_priority or None,
                article.highlight or None,
                article.highlight_image or None,
                article.highlight_image_name or None,
                article.materia_id or None,
                article.body_html or None,
                article.source_filename or None,
                article.source_zip or None,
                raw_payload_str,
                article.created_at.isoformat() if article.created_at else None,
                article.updated_at.isoformat() if article.updated_at else None,
            ))

        cursor.executemany(insert_sql, values)

    def _create_indexes(self, cursor):
        """Cria índices na tabela para melhorar performance de consultas."""
        # Índice no edition_date (já existe no modelo original)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_edition_date 
            ON imprensa_nacional_inlabsarticle(edition_date)
        """)
        
        # Índice no article_id
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_article_id 
            ON imprensa_nacional_inlabsarticle(article_id)
        """)
