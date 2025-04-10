from relationalDB import RelationalDB

db = RelationalDB()

db.create_table("topic_tbl",
    """\
    id INTEGER PRIMARY KEY,
            name TEXT\
    """)

db.create_table("web_content",
    """\
    id INTEGER PRIMARY KEY,
            url TEXT,
            content TEXT,
            dttm TEXT,      
            topic_id INTEGER NOT NULL,
            FOREIGN KEY (topic_id)
                REFERENCES topic_tbl (id)
                ON DELETE CASCADE ON UPDATE CASCADE\
    """)

tables = db.fetch(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
      AND name NOT LIKE 'sqlite_%'   -- skip SQLite’s internal tables
    ORDER BY name;
    """
)

for t in tables:
    print(t["name"])

db.close()
