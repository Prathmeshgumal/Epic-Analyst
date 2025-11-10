# ===========================
# SCHEMA EXTRACTOR CLASS
# ===========================

import psycopg2
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class SupabaseSchemaExtractor:
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish connection to Supabase PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(
                host=self.config['host'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                port=self.config['port']
            )
            self.cursor = self.conn.cursor()
            print("✅ Successfully connected to Supabase!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def get_all_tables(self) -> List[str]:
        """Get all user-defined tables (excluding system tables)"""
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        self.cursor.execute(query)
        tables = [row[0] for row in self.cursor.fetchall()]
        return tables

    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get detailed column information for a table"""
        query = """
        SELECT
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = %s
        ORDER BY ordinal_position;
        """
        self.cursor.execute(query, (table_name,))
        columns = []
        for row in self.cursor.fetchall():
            columns.append({
                'name': row[0],
                'type': row[1],
                'max_length': row[2],
                'nullable': row[3] == 'YES',
                'default': row[4]
            })
        return columns

    def get_primary_keys(self, table_name: str) -> List[str]:
        """Get primary key columns for a table"""
        query = """
        SELECT a.attname
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = %s::regclass
        AND i.indisprimary;
        """
        self.cursor.execute(query, (f'public.{table_name}',))
        return [row[0] for row in self.cursor.fetchall()]

    def get_foreign_keys(self, table_name: str) -> List[Dict[str, str]]:
        """Get foreign key relationships for a table"""
        query = """
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            rc.update_rule,
            rc.delete_rule
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        JOIN information_schema.referential_constraints AS rc
            ON rc.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_name = %s
        AND tc.table_schema = 'public';
        """
        self.cursor.execute(query, (table_name,))
        foreign_keys = []
        for row in self.cursor.fetchall():
            foreign_keys.append({
                'column': row[0],
                'references_table': row[1],
                'references_column': row[2],
                'on_update': row[3],
                'on_delete': row[4]
            })
        return foreign_keys

    def get_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """Get indexes for a table"""
        try:
            query = """
            SELECT
                i.relname AS index_name,
                array_agg(a.attname) AS column_names,
                ix.indisunique AS is_unique
            FROM pg_class t
            JOIN pg_index ix ON t.oid = ix.indrelid
            JOIN pg_class i ON i.oid = ix.indexrelid
            LEFT JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
            WHERE t.relname = %s
            AND t.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            AND i.relname NOT LIKE '%pkey'
            GROUP BY i.relname, ix.indisunique;
            """
            self.cursor.execute(query, (table_name,))
            indexes = []
            for row in self.cursor.fetchall():
                # row[1] is an array of column names
                columns = row[1] if row[1] else []
                indexes.append({
                    'name': row[0],
                    'columns': columns,  # Changed to plural since it can be multiple columns
                    'unique': row[2]
                })
            return indexes
        except Exception as e:
            print(f"⚠️  Could not fetch indexes from {table_name}: {e}")
            return []

    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample rows from a table"""
        try:
            query = f'SELECT * FROM "{table_name}" LIMIT %s;'
            self.cursor.execute(query, (limit,))
            columns = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()

            sample_data = []
            for row in rows:
                sample_data.append(dict(zip(columns, [str(val) if val is not None else None for val in row])))
            return sample_data
        except Exception as e:
            print(f"⚠️  Could not fetch sample data from {table_name}: {e}")
            return []

    def get_row_count(self, table_name: str) -> int:
        """Get total row count for a table"""
        try:
            query = f'SELECT COUNT(*) FROM "{table_name}";'
            self.cursor.execute(query)
            return self.cursor.fetchone()[0]
        except:
            return 0

    def extract_complete_schema(self) -> Dict[str, Any]:
        """Extract complete database schema with all metadata"""
        if not self.connect():
            return None

        print("\n🔍 Starting schema extraction...\n")

        tables = self.get_all_tables()
        print(f"📊 Found {len(tables)} tables: {', '.join(tables)}\n")

        schema = {
            'metadata': {
                'extracted_at': datetime.now().isoformat(),
                'database': self.config['database'],
                'host': self.config['host'],
                'total_tables': len(tables)
            },
            'tables': {}
        }

        for table_name in tables:
            print(f"📋 Processing table: {table_name}")

            columns = self.get_table_columns(table_name)
            primary_keys = self.get_primary_keys(table_name)
            foreign_keys = self.get_foreign_keys(table_name)
            indexes = self.get_indexes(table_name)
            row_count = self.get_row_count(table_name)
            sample_data = self.get_sample_data(table_name, limit=5)

            schema['tables'][table_name] = {
                'columns': columns,
                'primary_keys': primary_keys,
                'foreign_keys': foreign_keys,
                'indexes': indexes,
                'row_count': row_count,
                'sample_data': sample_data
            }

            print(f"  ✓ {len(columns)} columns, {row_count} rows")

        print("\n✅ Schema extraction complete!")
        return schema

    def generate_schema_summary(self, schema: Dict[str, Any]) -> str:
        """Generate a human-readable schema summary"""
        summary = []
        summary.append("=" * 80)
        summary.append("DATABASE SCHEMA SUMMARY")
        summary.append("=" * 80)
        summary.append(f"\nExtracted: {schema['metadata']['extracted_at']}")
        summary.append(f"Database: {schema['metadata']['database']}")
        summary.append(f"Total Tables: {schema['metadata']['total_tables']}")
        summary.append("\n" + "=" * 80)

        for table_name, table_info in schema['tables'].items():
            summary.append(f"\n📊 TABLE: {table_name}")
            summary.append(f"   Rows: {table_info['row_count']}")
            summary.append(f"   Primary Keys: {', '.join(table_info['primary_keys']) if table_info['primary_keys'] else 'None'}")

            summary.append(f"\n   Columns ({len(table_info['columns'])}):")
            for col in table_info['columns']:
                pk_marker = " 🔑" if col['name'] in table_info['primary_keys'] else ""
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                summary.append(f"      - {col['name']}: {col['type']} {nullable}{pk_marker}")

            if table_info['foreign_keys']:
                summary.append(f"\n   Foreign Keys:")
                for fk in table_info['foreign_keys']:
                    summary.append(f"      - {fk['column']} → {fk['references_table']}.{fk['references_column']}")

            if table_info['indexes']:
                summary.append(f"\n   Indexes:")
                unique_indexes = [idx for idx in table_info['indexes'] if idx['unique']]
                regular_indexes = [idx for idx in table_info['indexes'] if not idx['unique']]
                if unique_indexes:
                    for idx in unique_indexes:
                        cols = ', '.join(idx.get('columns', [idx.get('column', 'unknown')]))
                        summary.append(f"      Unique: {idx['name']} on ({cols})")
                if regular_indexes:
                    for idx in regular_indexes:
                        cols = ', '.join(idx.get('columns', [idx.get('column', 'unknown')]))
                        summary.append(f"      Regular: {idx['name']} on ({cols})")

            summary.append("\n" + "-" * 80)

        return "\n".join(summary)

    def save_schema(self, schema: Dict[str, Any], filename: str = 'schema.json'):
        """Save schema to JSON file"""
        with open(filename, 'w') as f:
            json.dump(schema, f, indent=2, default=str)
        print(f"\n💾 Schema saved to: {filename}")

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("\n🔌 Connection closed")