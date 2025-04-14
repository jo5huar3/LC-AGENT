from relationalDB import RelationalDB
from datetime import datetime, timezone

db = RelationalDB()

db.create_table("topic_tbl",
    """\
    id INTEGER PRIMARY KEY,
            topic_name TEXT\
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

#db.insert("topic_tbl", {"topic_name": "App Engine"})

#dttm = datetime.now(timezone.utc).isoformat(timespec="seconds")

dttm = datetime.now()

#db.insert("web_content", {"url": "TEST", "content": "TEST", "dttm": dttm, "topic_id" : "1"})

print(db.newFetch("topic_tbl"))

print(db.newFetch("web_content"))

#print(db.fetch("PRAGMA table_info(topic_tbl);"))
# → [{'cid': 0, 'name': 'id', ...}, …]   # you will not see 'topic_name'


db.close()
