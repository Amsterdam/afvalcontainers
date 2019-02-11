import logging

LOG = logging.getLogger(__name__)


def fix_table(connection, table):

    max_id = f"select max(id) from {table}"

    data = connection.execute(max_id).fetchall()
    table_count = data[0][0] or 0
    new_max = table_count + 1

    has_default = f"""
    SELECT column_name, column_default
    FROM information_schema.columns
    WHERE (table_schema, table_name) = ('public', '{table}')
    and column_name = 'id';
    """

    data = connection.execute(has_default).fetchall()
    LOG.error(data)

    if data[0][1] is not None:
        LOG.info("No fix needed")
        return

    new_seq_name = f"{table}_sequence"

    new_sequence = f"""
    create sequence if not exists {new_seq_name}
    start {new_max};
    """

    new_owner = f"""
    alter sequence {new_seq_name} owner to kilogram;
    alter sequence {new_seq_name} owned by {table}.id;
    """

    LOG.info(new_sequence)
    LOG.info(new_owner)

    connection.execute(new_sequence)
    connection.execute(new_owner)

    alter_seq = f"""
    alter table {table} alter column id
    set default nextval('{new_seq_name}');
    """

    connection.execute(alter_seq)
    LOG.info(alter_seq)
