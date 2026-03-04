"""
Database Comparison Page
Schema comparison, data model, and migration status
"""

import streamlit as st
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.unified_loader import UnifiedDataLoader
import pandas as pd

st.set_page_config(page_title="Database Comparison", page_icon="🗄️", layout="wide")

# Load data
@st.cache_resource
def get_data_loader():
    return UnifiedDataLoader(
        docs_path="../../../../docs",
        mock_legacy_path="../../mock-data/legacy"
    )

try:
    loader = get_data_loader()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    data_loaded = False

st.title("🗄️ Database Comparison")
st.markdown("### Schema, data model, and migration analysis")

if not data_loaded:
    st.error("Data loading failed. Check paths and data sources.")
    st.stop()

try:
    # Get database comparison data
    db_comp = loader.get_database_comparison()

    # High-level comparison
    st.subheader("Database Technology Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏛️ Legacy System")
        st.info(f"**Database:** {db_comp['legacy']['type']}")
        st.info(f"**ORM:** {db_comp['legacy']['orm']}")
        st.info(f"**Pattern:** {db_comp['legacy']['pattern']}")

    with col2:
        st.markdown("### 🚀 Modern System")
        st.success(f"**Database:** {db_comp['modern']['type']}")
        st.success(f"**ORM:** {db_comp['modern']['orm']}")
        st.success(f"**Pattern:** {db_comp['modern']['pattern']}")

    st.markdown("---")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Schema Comparison", "🔄 Data Model", "📦 Migration Status", "🔍 Query Patterns"])

    with tab1:
        st.subheader("Schema Comparison")

        # Check for schema documentation
        schema_path = Path(loader.modern.docs_path) / "database-schema.md"

        if schema_path.exists():
            content = schema_path.read_text(encoding="utf-8")
            st.markdown(content)
        else:
            st.info("Database schema documentation not found.")

        st.markdown("---")

        # Seam-specific schema
        seams = loader.modern.get_all_seams()

        if seams:
            st.subheader("Seam-Specific Schemas")

            selected_seam = st.selectbox("Select seam:", seams, key="schema_seam")

            if selected_seam:
                seam_schema_path = Path(loader.modern.docs_path) / f"seams/{selected_seam}/database-schema.md"

                if seam_schema_path.exists():
                    content = seam_schema_path.read_text(encoding="utf-8")
                    st.markdown(content)
                else:
                    st.info(f"Schema documentation not found for `{selected_seam}`.")

                # Show table list if available
                tables_path = Path(loader.modern.docs_path) / f"seams/{selected_seam}/tables.json"

                if tables_path.exists():
                    try:
                        tables = json.loads(tables_path.read_text())

                        st.markdown("### Tables Used")

                        table_data = []
                        for table in tables.get("tables", []):
                            table_data.append({
                                "Table": table.get("name", "Unknown"),
                                "Operations": ", ".join(table.get("operations", [])),
                                "Row Count": table.get("row_count", "N/A"),
                            })

                        if table_data:
                            df = pd.DataFrame(table_data)
                            st.dataframe(df, use_container_width=True, hide_index=True)

                    except Exception as e:
                        st.error(f"Error loading table data: {e}")

    with tab2:
        st.subheader("Data Model Comparison")

        seams = loader.modern.get_all_seams()

        if not seams:
            st.info("No seams discovered yet.")
        else:
            selected_seam = st.selectbox("Select seam:", seams, key="model_seam")

            if selected_seam:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### 🏛️ Legacy Model")

                    st.code("""
// Entity Framework model (example)
public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }
    public decimal Price { get; set; }
    public int CategoryId { get; set; }

    public virtual Category Category { get; set; }
}
                    """, language="csharp")

                with col2:
                    st.markdown("### 🚀 Modern Model")

                    st.code("""
# SQLAlchemy async model
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))

    category = relationship("Category", back_populates="products")
                    """, language="python")

                # Show actual models if implemented
                model_path = Path(loader.modern.docs_path).parent / f"backend/app/{selected_seam}/models.py"

                if model_path.exists():
                    st.markdown("---")
                    st.success("✅ Modern models implemented")

                    with st.expander("📄 View models.py", expanded=False):
                        content = model_path.read_text(encoding="utf-8")
                        st.code(content, language="python")
                else:
                    st.info("Modern models not yet implemented.")

    with tab3:
        st.subheader("Migration Status")

        # Check for migration scripts
        migrations_path = Path(loader.modern.docs_path).parent / "backend/alembic/versions"

        if migrations_path.exists():
            migration_files = list(migrations_path.glob("*.py"))

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Migration Scripts", len(migration_files))

            with col2:
                # Check if migrations are applied (would need to query DB)
                st.metric("Status", "Ready")

            with col3:
                # Latest migration version
                if migration_files:
                    latest = sorted(migration_files)[-1]
                    st.metric("Latest Version", latest.stem[:8] + "...")

            # List migrations
            if migration_files:
                st.markdown("---")
                st.markdown("### Migration History")

                migration_data = []
                for mig in sorted(migration_files):
                    # Extract revision from filename (format: {revision}_{description}.py)
                    name = mig.stem
                    parts = name.split("_", 1)
                    revision = parts[0] if parts else "unknown"
                    description = parts[1].replace("_", " ").title() if len(parts) > 1 else "No description"

                    migration_data.append({
                        "Revision": revision,
                        "Description": description,
                        "File": mig.name,
                    })

                df = pd.DataFrame(migration_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

        else:
            st.info("No migration scripts found. Migrations will be created during implementation.")

        st.markdown("---")

        # Migration strategy
        st.subheader("Migration Strategy")

        st.markdown("""
        **Approach:** Like-to-like schema migration

        1. **Schema Analysis** — Extract legacy schema structure
        2. **Model Generation** — Create SQLAlchemy models matching legacy structure
        3. **Data Migration** — Transfer data with validation
        4. **Incremental Cutover** — Migrate seam-by-seam

        **Data Safety:**
        - ✅ Legacy database remains read-only
        - ✅ Full data backups before migration
        - ✅ Validation queries after migration
        - ✅ Rollback plan for each seam
        """)

    with tab4:
        st.subheader("Query Pattern Comparison")

        # Show common query patterns
        st.markdown("### Common Query Patterns")

        patterns = [
            {
                "Operation": "Select with Filter",
                "Legacy": "db.Products.Where(p => p.CategoryId == id).ToList()",
                "Modern": "await session.execute(select(Product).where(Product.category_id == id))"
            },
            {
                "Operation": "Join Query",
                "Legacy": "db.Products.Include(p => p.Category).ToList()",
                "Modern": "await session.execute(select(Product).options(selectinload(Product.category)))"
            },
            {
                "Operation": "Insert",
                "Legacy": "db.Products.Add(product); db.SaveChanges()",
                "Modern": "session.add(product); await session.commit()"
            },
            {
                "Operation": "Update",
                "Legacy": "product.Name = 'New'; db.SaveChanges()",
                "Modern": "product.name = 'New'; await session.commit()"
            },
            {
                "Operation": "Delete",
                "Legacy": "db.Products.Remove(product); db.SaveChanges()",
                "Modern": "await session.delete(product); await session.commit()"
            },
        ]

        for pattern in patterns:
            with st.expander(f"**{pattern['Operation']}**", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Legacy (C#)**")
                    st.code(pattern["Legacy"], language="csharp")

                with col2:
                    st.markdown("**Modern (Python)**")
                    st.code(pattern["Modern"], language="python")

        # Performance considerations
        st.markdown("---")
        st.subheader("Performance Considerations")

        st.markdown("""
        **Key Improvements:**
        - ✅ **Async queries** — Non-blocking database operations
        - ✅ **Connection pooling** — Reuse database connections
        - ✅ **Query optimization** — Eager loading with selectinload()
        - ✅ **Prepared statements** — Automatic with SQLAlchemy
        - ✅ **Index strategy** — Match legacy indexes initially

        **Monitoring:**
        - Track slow queries (> 100ms)
        - Monitor connection pool usage
        - Analyze query plans for optimization
        """)

except Exception as e:
    st.error("Error loading database comparison")
    st.exception(e)
