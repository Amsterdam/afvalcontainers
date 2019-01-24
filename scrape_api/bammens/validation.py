"""
collect and validate table counts
"""
import logging

log = logging.getLogger(__name__)


def validate_counts(table_counts, session):
    """Validata table total counts"""
    failed = False

    for tablename, target_count in table_counts:
        sql = f"select count(*) from {tablename}"
        data = session.execute(sql).fetchall()

        table_count = data[0][0]
        if table_count < target_count:
            failed = True
            log.error(
                '\n\n\n FAILED Count %s %d is not > %d \n\n',
                tablename, table_count, target_count)
        else:
            log.info(
                'Count OK %s %d > %d',
                tablename, table_count, target_count)

    if failed:
        raise ValueError('Table counts not at target!')


def validate_attribute_counts(validate_sql, session):
    """Validate count from custom sql queries"""
    for sql, min_expected, max_expected in validate_sql:
        data = session.execute(sql).fetchall()
        table_count = data[0][0]
        failed = False

        if min_expected >= table_count >= max_expected:
            failed = True
            log.error(
                '\n\n\n FAILED %s %d < %d \n\n',
                sql, table_count, max_expected)
        else:
            log.info(
                'Count OK %s %d < %d',
                sql, table_count, max_expected)

    if failed:
        raise ValueError('Table counts not within range!')
