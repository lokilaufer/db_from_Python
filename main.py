import psycopg2


def create_db(conn):
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                phone TEXT[]
            )
        ''')
        conn.commit()


def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO clients (first_name, last_name, email, phone)
            VALUES (%s, %s, %s, %s)
        ''', (first_name, last_name, email, phones))
        conn.commit()


def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute('''
            UPDATE clients
            SET phone = phone || %s
            WHERE id = %s
        ''', (phone, client_id))
        conn.commit()


def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    update_fields = []
    if first_name:
        update_fields.append('first_name = %s')
    if last_name:
        update_fields.append('last_name = %s')
    if email:
        update_fields.append('email = %s')
    if phones:
        update_fields.append('phone = %s')

    update_query = ', '.join(update_fields)

    with conn.cursor() as cur:
        cur.execute(f'''
            UPDATE clients
            SET {update_query}
            WHERE id = %s
        ''', (first_name, last_name, email, phones, client_id))
        conn.commit()


def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute('''
            UPDATE clients
            SET phone = array_remove(phone, %s)
            WHERE id = %s
        ''', (phone, client_id))
        conn.commit()


def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute('''
            DELETE FROM clients
            WHERE id = %s
        ''', (client_id,))
        conn.commit()


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    query = '''
        SELECT * FROM clients
        WHERE first_name = %s OR last_name = %s OR email = %s OR phone @> %s
    '''
    parameters = (first_name, last_name, email, [phone] if phone else [])

    with conn.cursor() as cur:
        cur.execute(query, parameters)
        return cur.fetchall()


# Connect to the database
conn = psycopg2.connect(database="clients_db", user="postgres", password="postgres")

# Create the database structure
create_db(conn)

# Add a new client
add_client(conn, 'John', 'Doe', 'john.doe@example.com', ['1234567890'])

# Add a phone for an existing client
add_phone(conn, 1, '9876543210')

# Update client information
change_client(conn, 1, first_name='Jane', last_name='Smith')

# Delete a phone for a client
delete_phone(conn, 1, '1234567890')

# Delete a client
delete_client(conn, 1)

# Find a client by email
result = find_client(conn, email='jane.smith@example.com')
print(result)

conn.close()
