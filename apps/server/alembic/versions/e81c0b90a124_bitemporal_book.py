"""Bitemporal book history and immutable event enforcement.

Legacy current state is checkpointed at migration time. Earlier history is unknown.
"""
from alembic import op
import sqlalchemy as sa

revision = "e81c0b90a124"
down_revision = "d7b2c4e81f03"
branch_labels = None
depends_on = None


def upgrade():
    for table in ("households", "lots", "book_events"):
        for column in ("valid_time", "recorded_time"):
            op.add_column(table, sa.Column(column, sa.DateTime(timezone=True),
                                          nullable=False, server_default=sa.func.now()))
    op.create_index("ix_book_events_temporal", "book_events",
                    ["household_id", "valid_time", "recorded_time"])
    op.create_unique_constraint("uq_book_events_household_seq", "book_events",
                                ["household_id", "seq"])
    # A baseline records only the current state actually known at migration.
    op.execute("""
    INSERT INTO book_events (id, household_id, event_type, payload, seq,
                             idempotency_key, created_at, valid_time, recorded_time)
    SELECT 'baseline_' || h.id, h.id, 'book.snapshot',
      jsonb_build_object('household_id', h.id, 'household_name', h.name,
        'as_of', h.as_of, 'tax', h.tax,
        'lots', COALESCE((SELECT jsonb_agg(jsonb_build_object(
            'id', l.id, 'symbol', l.symbol, 'name', l.name, 'asset_class', l.asset_class,
            'sector', l.sector, 'quantity', l.quantity, 'cost', l.cost, 'price', l.price,
            'acquired_on', l.acquired_on, 'fmv_2018', l.fmv_2018) ORDER BY l.id)
          FROM lots l WHERE l.household_id = h.id), '[]'::jsonb)),
      COALESCE((SELECT MAX(seq) FROM book_events e WHERE e.household_id=h.id), 0)+1,
      'baseline_' || h.id, now(), now(), now()
    FROM households h
    """)
    op.execute("""
    CREATE FUNCTION enforce_book_event_immutability() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE previous_time timestamptz; previous_seq integer;
    BEGIN
      IF TG_OP <> 'INSERT' THEN
        RAISE EXCEPTION 'book_events is append-only';
      END IF;
      PERFORM pg_advisory_xact_lock(hashtextextended('book:' || NEW.household_id, 0));
      SELECT recorded_time, seq INTO previous_time, previous_seq FROM book_events
        WHERE household_id=NEW.household_id ORDER BY seq DESC LIMIT 1;
      IF previous_time IS NOT NULL AND NEW.recorded_time <= previous_time THEN
        RAISE EXCEPTION 'recorded_time must increase';
      END IF;
      IF NEW.seq <> COALESCE(previous_seq, 0)+1 THEN
        RAISE EXCEPTION 'event sequence must be contiguous';
      END IF;
      RETURN NEW;
    END $$;
    """)
    op.execute("""
    CREATE TRIGGER immutable_book_events BEFORE INSERT OR UPDATE OR DELETE ON book_events
      FOR EACH ROW EXECUTE FUNCTION enforce_book_event_immutability();
    """)


def downgrade():
    op.execute("DROP TRIGGER immutable_book_events ON book_events")
    op.execute("DROP FUNCTION enforce_book_event_immutability()")
    op.drop_constraint("uq_book_events_household_seq", "book_events", type_="unique")
    op.drop_index("ix_book_events_temporal", table_name="book_events")
    for table in ("households", "lots", "book_events"):
        op.drop_column(table, "recorded_time")
        op.drop_column(table, "valid_time")
