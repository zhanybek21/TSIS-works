import json
import csv
from connect import get_connection

def add_contact(conn, name, email, birthday, group_name):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
            group = cur.fetchone()
            if not group:
                cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
                group_id = cur.fetchone()[0]
            else:
                group_id = group[0]

            bday_val = birthday if birthday else None

            cur.execute("""
                INSERT INTO contacts (name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
            """, (name, email, bday_val, group_id))
            conn.commit()
    except Exception:
        conn.rollback()

def call_add_phone(conn, name, phone, p_type):
    try:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, p_type))
            conn.commit()
    except Exception:
        conn.rollback()

def paginated_view(conn, filter_group=None, search_email=None, sort_by='name'):
    limit = 3
    offset = 0
    
    while True:
        with conn.cursor() as cur:
            query = """
                SELECT c.name, c.email, c.birthday, g.name, string_agg(p.phone || ' (' || p.type || ')', ', ')
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON c.id = p.contact_id
                WHERE 1=1
            """
            params = []
            if filter_group:
                query += " AND g.name ILIKE %s"
                params.append(filter_group)
            if search_email:
                query += " AND c.email ILIKE %s"
                params.append(f"%{search_email}%")
            
            query += " GROUP BY c.id, g.name"
            
            if sort_by == 'birthday': query += " ORDER BY c.birthday NULLS LAST"
            elif sort_by == 'date': query += " ORDER BY c.created_at"
            else: query += " ORDER BY c.name"
            
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            
            if not rows:
                print("Пусто.")
            else:
                for r in rows:
                    print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")
            
        cmd = input("\n[n]ext, [p]rev, [q]uit: ").strip().lower()
        if cmd == 'n': 
            if len(rows) == limit: offset += limit
        elif cmd == 'p': 
            offset = max(0, offset - limit)
        elif cmd == 'q': 
            break

def export_json(conn, filename="contacts.json"):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, c.email, TO_CHAR(c.birthday, 'YYYY-MM-DD'), g.name as group,
                COALESCE(json_agg(json_build_object('phone', p.phone, 'type', p.type)) FILTER (WHERE p.phone IS NOT NULL), '[]')
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON c.id = p.contact_id
                GROUP BY c.id, g.name
            """)
            rows = cur.fetchall()
            data = [{"name": r[0], "email": r[1], "birthday": r[2], "group": r[3], "phones": r[4]} for r in rows]
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

def import_json(conn, filename="contacts.json"):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        with conn.cursor() as cur:
            for item in data:
                cur.execute("SELECT id FROM contacts WHERE name = %s", (item['name'],))
                exists = cur.fetchone()
                
                if exists:
                    action = input(f"[s]kip / [o]verwrite? ").lower()
                    if action == 's':
                        continue
                    elif action == 'o':
                        cur.execute("DELETE FROM contacts WHERE name = %s", (item['name'],))
                
                add_contact(conn, item['name'], item.get('email'), item.get('birthday'), item.get('group', 'Other'))
                for phone in item.get('phones', []):
                    call_add_phone(conn, item['name'], phone['phone'], phone['type'])
    except Exception:
        pass

def main():
    conn = get_connection()
    if not conn:
        return

    while True:
        print("\n1. Добавить контакт\n2. Добавить телефон\n3. Изменить группу\n4. Просмотр\n5. Экспорт\n6. Импорт\n7. Поиск\n0. Выход")
        choice = input("Выбор: ")
        
        if choice == '1':
            add_contact(conn, input("Имя: "), input("Email: "), input("ДР (YYYY-MM-DD): "), input("Группа: ") or 'Other')
        elif choice == '2':
            call_add_phone(conn, input("Имя: "), input("Телефон: "), input("Тип (home/work/mobile): "))
        elif choice == '3':
            try:
                with conn.cursor() as cur:
                    cur.execute("CALL move_to_group(%s, %s)", (input("Имя: "), input("Группа: ")))
                    conn.commit()
            except Exception:
                conn.rollback()
        elif choice == '4':
            paginated_view(conn, input("Группа: ") or None, input("Email: ") or None, input("Сортировка: ") or 'name')
        elif choice == '5':
            export_json(conn)
        elif choice == '6':
            import_json(conn)
        elif choice == '7':
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM search_contacts_ext(%s)", (input("Текст: "),))
                for r in cur.fetchall(): print(f"{r[0]} | {r[1]} | {r[2]}")
        elif choice == '0':
            break
            
    conn.close()

if __name__ == "__main__":
    main()