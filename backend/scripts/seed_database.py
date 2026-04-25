"""
seed_database.py — High-performance database seeder with mandatory data cleaning.

Pipeline:
  1. Load CSV into pandas
  2. Execute comprehensive data cleaning & preprocessing
  3. Deduplicate stores/products in-memory (no per-row DB queries)
  4. Bulk-insert all entities using SQLAlchemy bulk_insert_mappings
"""
import pandas as pd
import numpy as np
import sys
import os
import time
import logging
from sqlalchemy.orm import Session

# Add the backend directory to sys.path so we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import db_manager, Base
from app.db.models.retail import Store, Product, Transaction

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../Dataset/Retail_Sales_Data.csv')
)

BATCH_SIZE = 5000


# ── Data Cleaning & Preprocessing Pipeline ──────────────────────────────────

def clean_and_preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mandatory data cleaning pipeline. Steps:
      1. Standardize string columns (strip, title-case, fill nulls)
      2. Drop rows missing critical fields (Date, Revenue)
      3. Remove anomalous rows (negative Revenue or Unit_Price)
      4. Fill non-critical numerical nulls (Store_Rating → median, Discount → 0)
      5. Drop exact duplicate rows
      6. Downcast numeric dtypes for memory efficiency
    """
    logger.info("┌─ Data Cleaning & Preprocessing Pipeline ─────────────────")
    initial_rows = len(df)

    # ── Step 1: Standardize string columns ──────────────────────────────
    string_cols = df.select_dtypes(include=['object']).columns
    for col in string_cols:
        df[col] = (
            df[col]
            .fillna('Unknown')
            .astype(str)
            .str.strip()
            .str.title()
        )
        df[col] = df[col].replace({'Nan': 'Unknown', 'None': 'Unknown', '': 'Unknown'})
    logger.info(f"│  ✓ Standardized {len(string_cols)} string columns")

    # ── Step 2: Drop rows with missing critical data ────────────────────
    critical_cols = [c for c in ['Date', 'Timestamp', 'Revenue'] if c in df.columns]
    before = len(df)
    if critical_cols:
        df.dropna(subset=critical_cols, inplace=True)
    dropped_critical = before - len(df)
    logger.info(f"│  ✓ Dropped {dropped_critical} rows missing critical fields {critical_cols}")

    # ── Step 3: Remove anomalous rows ───────────────────────────────────
    before = len(df)
    if 'Revenue' in df.columns:
        df = df[df['Revenue'] >= 0]
    if 'Unit_Price' in df.columns:
        df = df[df['Unit_Price'] >= 0]
    dropped_anomalies = before - len(df)
    logger.info(f"│  ✓ Removed {dropped_anomalies} anomalous rows (negative Revenue/Price)")

    # ── Step 4: Fill non-critical numerical nulls ───────────────────────
    if 'Store_Rating' in df.columns:
        median_rating = df['Store_Rating'].median()
        filled_rating = df['Store_Rating'].isna().sum()
        df['Store_Rating'] = df['Store_Rating'].fillna(median_rating)
        logger.info(f"│  ✓ Filled {filled_rating} null Store_Ratings with median ({median_rating:.2f})")

    if 'Discount_Percentage' in df.columns:
        filled_disc = df['Discount_Percentage'].isna().sum()
        df['Discount_Percentage'] = df['Discount_Percentage'].fillna(0.0)
        logger.info(f"│  ✓ Filled {filled_disc} null Discount_Percentages with 0.0")

    # ── Step 5: Drop exact duplicate rows ───────────────────────────────
    before = len(df)
    df.drop_duplicates(inplace=True)
    dropped_dupes = before - len(df)
    logger.info(f"│  ✓ Dropped {dropped_dupes} exact duplicate rows")

    # ── Step 6: Downcast numeric dtypes for memory efficiency ───────────
    float_cols = df.select_dtypes(include=['float64']).columns
    for col in float_cols:
        df[col] = pd.to_numeric(df[col], downcast='float')

    int_cols = df.select_dtypes(include=['int64']).columns
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], downcast='integer')

    mem_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)
    final_rows = len(df)
    logger.info(f"│  ✓ Downcasted numeric dtypes. Memory: {mem_mb:.2f} MB")
    logger.info(
        f"└─ Pipeline complete: {initial_rows} → {final_rows} rows "
        f"({initial_rows - final_rows} removed)"
    )

    return df.reset_index(drop=True)


# ── Bulk Seeding Logic ───────────────────────────────────────────────────────

def seed_database():
    if not os.path.exists(CSV_PATH):
        logger.error(f"CSV file not found at {CSV_PATH}")
        return

    t0 = time.perf_counter()

    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=db_manager.engine)

    logger.info(f"Loading data from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    logger.info(f"Loaded {len(df)} rows × {len(df.columns)} columns")

    # ── Execute mandatory cleaning pipeline ─────────────────────────────
    df = clean_and_preprocess(df)

    session: Session = db_manager.SessionLocal()

    try:
        # ── 1. Seed Stores (in-memory dedup, single bulk insert) ────────
        logger.info("Seeding Stores...")
        if 'Store_Location' in df.columns:
            store_cols = ['Store_Location']
            if 'Store_Rating' in df.columns:
                store_cols.append('Store_Rating')

            unique_stores_df = df[store_cols].drop_duplicates(subset=['Store_Location'])
            store_mappings = []
            for _, row in unique_stores_df.iterrows():
                store_mappings.append({
                    'store_location': row['Store_Location'],
                    'store_rating': row.get('Store_Rating', 0.0),
                })

            session.bulk_insert_mappings(Store, store_mappings)
            session.commit()
            logger.info(f"  → Inserted {len(store_mappings)} unique stores")

            # Build location → id map from DB
            all_stores = session.query(Store.id, Store.store_location).all()
            store_map = {loc: sid for sid, loc in all_stores}
        else:
            logger.warning("Store_Location not found. Creating default store.")
            session.bulk_insert_mappings(Store, [{'store_location': 'Default_Location', 'store_rating': 0.0}])
            session.commit()
            store_map = {'Default_Location': session.query(Store).first().id}
            df['Store_Location'] = 'Default_Location'

        # ── 2. Seed Products (in-memory dedup, single bulk insert) ──────
        logger.info("Seeding Products...")
        prod_cols = ['Product_Category', 'Unit_Price']
        opt_cols = ['Product_Subcategory', 'Brand', 'Stock_On_Hand']
        for c in opt_cols:
            if c in df.columns:
                prod_cols.append(c)

        if 'Product_Category' in df.columns and 'Unit_Price' in df.columns:
            unique_products_df = df[prod_cols].drop_duplicates()
            product_mappings = []
            for _, row in unique_products_df.iterrows():
                product_mappings.append({
                    'category': row['Product_Category'],
                    'unit_price': float(row['Unit_Price']),
                    'subcategory': row.get('Product_Subcategory'),
                    'brand': row.get('Brand'),
                    'stock_on_hand': int(row.get('Stock_On_Hand', 0)),
                })

            session.bulk_insert_mappings(Product, product_mappings)
            session.commit()
            logger.info(f"  → Inserted {len(product_mappings)} unique products")

            # Build (cat, subcat, brand, price) → id map from DB
            all_products = session.query(
                Product.id, Product.category, Product.subcategory,
                Product.brand, Product.unit_price
            ).all()
            product_map = {
                (p.category, p.subcategory, p.brand, p.unit_price): p.id
                for p in all_products
            }
        else:
            logger.warning("Product_Category column missing. Creating default product.")
            session.bulk_insert_mappings(Product, [{'category': 'Default', 'unit_price': 10.0}])
            session.commit()
            product_map = {('Default', None, None, 10.0): session.query(Product).first().id}
            df['Product_Category'] = 'Default'
            df['Unit_Price'] = 10.0

        # ── 3. Seed Transactions (vectorized build + batched bulk insert) ─
        logger.info("Seeding Transactions (bulk)...")

        has_subcat = 'Product_Subcategory' in df.columns
        has_brand = 'Brand' in df.columns

        txn_mappings = []
        skipped = 0

        for idx in range(len(df)):
            row = df.iloc[idx]
            store_loc = row.get('Store_Location', 'Default_Location')
            s_id = store_map.get(store_loc)

            cat = row.get('Product_Category', 'Default')
            subcat = row['Product_Subcategory'] if has_subcat else None
            brand = row['Brand'] if has_brand else None
            price = float(row.get('Unit_Price', 10.0))

            p_id = product_map.get((cat, subcat, brand, price))

            if s_id is None or p_id is None:
                skipped += 1
                continue

            timestamp_val = row.get('Date') or row.get('Timestamp') or pd.Timestamp.now()

            txn_mappings.append({
                'store_id': int(s_id),
                'product_id': int(p_id),
                'timestamp': pd.to_datetime(timestamp_val),
                'discount_percentage': float(row.get('Discount_Percentage', 0.0)),
                'revenue': float(row.get('Revenue', 0.0)),
                'customer_type': str(row.get('Customer_Type', 'Unknown')),
                'payment_mode': str(row.get('Payment_Mode', 'Unknown')),
                'promotion_applied': bool(row.get('Promotion_Applied', False)),
                'holiday_flag': bool(row.get('Holiday_Flag', False)),
            })

            # Flush in batches to prevent memory buildup
            if len(txn_mappings) >= BATCH_SIZE:
                session.bulk_insert_mappings(Transaction, txn_mappings)
                session.commit()
                txn_mappings = []

        # Flush remaining
        if txn_mappings:
            session.bulk_insert_mappings(Transaction, txn_mappings)
            session.commit()

        elapsed = time.perf_counter() - t0
        total_txns = session.query(Transaction).count()
        logger.info(f"  → Inserted {total_txns} transactions (skipped {skipped})")
        logger.info(f"✅ Database seeding completed in {elapsed:.1f}s")

    except Exception as e:
        session.rollback()
        logger.error(f"Error during seeding: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
