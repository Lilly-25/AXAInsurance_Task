#!/usr/bin/env python3
"""
Working script to extract Titanic data and generate PostgreSQL init script
"""

import sqlite3
import pandas as pd
from pathlib import Path
import sys

def main():
    print("=== TITANIC DATA EXTRACTOR ===")
    print("Starting data extraction...")
    
    try:
        # Connect to SQLite database
        db_path = "../data/titanic.db"
        if not Path(db_path).exists():
            print(f"ERROR: Database file {db_path} not found!")
            return False
            
        print(f"Connecting to {db_path}...")
        conn = sqlite3.connect(db_path)
        
        # Your comprehensive JOIN query from the notebook
        query = """
        SELECT 
            o.survived,
            o.pclass,
            s.sex,
            o.age,
            o.sibsp,
            o.parch,
            o.fare,
            o.adult_male,
            o.alone,
            e.embarked,
            c.class,
            w.who,
            d.deck,
            et.embark_town,
            a.alive
        FROM Observation o
        LEFT JOIN Sex s ON o.sex_id = s.sex_id
        LEFT JOIN Embarked e ON o.embarked_id = e.embarked_id
        LEFT JOIN Class c ON o.class_id = c.class_id
        LEFT JOIN Who w ON o.who_id = w.who_id
        LEFT JOIN Deck d ON o.deck_id = d.deck_id
        LEFT JOIN EmbarkTown et ON o.embark_town_id = et.embark_town_id
        LEFT JOIN Alive a ON o.alive_id = a.alive_id
        ORDER BY o.ROWID
        """
        
        print("Executing JOIN query from notebook...")
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        print(f"SUCCESS: Extracted {len(df)} records")
        print(f"Survivors: {df['survived'].sum()}/{len(df)} ({df['survived'].mean()*100:.1f}%)")
        
        # Generate PostgreSQL init script that recreates the original normalized structure
        output_file = "../sql/init_db.sql"
        print(f"Generating PostgreSQL script: {output_file}")
        
        sql_content = """-- PostgreSQL Initialisierung mit echten Titanic-Daten
-- Automatisch generiert aus titanic.db

-- Lookup-Tabellen erstellen
CREATE TABLE IF NOT EXISTS Sex (
    sex_id SERIAL PRIMARY KEY,
    sex VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS Embarked (
    embarked_id SERIAL PRIMARY KEY,
    embarked VARCHAR(1)
);

CREATE TABLE IF NOT EXISTS Class (
    class_id SERIAL PRIMARY KEY,
    class VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS Who (
    who_id SERIAL PRIMARY KEY,
    who VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS Deck (
    deck_id SERIAL PRIMARY KEY,
    deck VARCHAR(1)
);

CREATE TABLE IF NOT EXISTS EmbarkTown (
    embark_town_id SERIAL PRIMARY KEY,
    embark_town VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS Alive (
    alive_id SERIAL PRIMARY KEY,
    alive VARCHAR(5)
);

-- Haupt-Observation-Tabelle erstellen
CREATE TABLE IF NOT EXISTS Observation (
    id SERIAL PRIMARY KEY,
    survived INTEGER NOT NULL,
    pclass INTEGER NOT NULL,
    age FLOAT,
    sibsp INTEGER NOT NULL,
    parch INTEGER NOT NULL,
    fare FLOAT,
    adult_male BOOLEAN NOT NULL,
    alone BOOLEAN NOT NULL,
    sex_id INTEGER REFERENCES Sex(sex_id),
    embarked_id INTEGER REFERENCES Embarked(embarked_id),
    class_id INTEGER REFERENCES Class(class_id),
    who_id INTEGER REFERENCES Who(who_id),
    deck_id INTEGER REFERENCES Deck(deck_id),
    embark_town_id INTEGER REFERENCES EmbarkTown(embark_town_id),
    alive_id INTEGER REFERENCES Alive(alive_id)
);

-- Lookup-Daten einfügen
INSERT INTO Sex (sex_id, sex) VALUES (0, 'female'), (1, 'male');
INSERT INTO Embarked (embarked_id, embarked) VALUES (-1, NULL), (0, 'C'), (1, 'Q'), (2, 'S');
INSERT INTO Class (class_id, class) VALUES (0, 'First'), (1, 'Second'), (2, 'Third');
INSERT INTO Who (who_id, who) VALUES (0, 'child'), (1, 'man'), (2, 'woman');
INSERT INTO Deck (deck_id, deck) VALUES (-1, NULL), (0, 'A'), (1, 'B'), (2, 'C'), (3, 'D'), (4, 'E'), (5, 'F'), (6, 'G'), (7, 'T');
INSERT INTO EmbarkTown (embark_town_id, embark_town) VALUES (-1, NULL), (0, 'Cherbourg'), (1, 'Queenstown'), (2, 'Southampton');
INSERT INTO Alive (alive_id, alive) VALUES (0, 'no'), (1, 'yes');

-- Observation-Daten einfügen
INSERT INTO Observation (survived, pclass, age, sibsp, parch, fare, adult_male, alone, sex_id, embarked_id, class_id, who_id, deck_id, embark_town_id, alive_id) VALUES
"""
        
        # Generate observation data rows with proper foreign keys
        rows = []
        for _, row in df.iterrows():
            # Map values to foreign keys
            sex_id = 1 if row['sex'] == 'male' else 0
            
            # Map embarked
            embarked_map = {None: -1, 'C': 0, 'Q': 1, 'S': 2}
            embarked_id = embarked_map.get(row['embarked'], -1)
            
            # Map class
            class_map = {'First': 0, 'Second': 1, 'Third': 2}
            class_id = class_map.get(row['class'], 2)
            
            # Map who
            who_map = {'child': 0, 'man': 1, 'woman': 2}
            who_id = who_map.get(row['who'], 1)
            
            # Map deck
            deck_map = {None: -1, 'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'T': 7}
            deck_id = deck_map.get(row['deck'], -1)
            
            # Map embark_town
            embark_town_map = {None: -1, 'Cherbourg': 0, 'Queenstown': 1, 'Southampton': 2}
            embark_town_id = embark_town_map.get(row['embark_town'], -1)
            
            # Map alive
            alive_id = 1 if row['alive'] == 'yes' else 0
            
            # Handle NULL values
            age = f"{row['age']:.2f}" if pd.notnull(row['age']) else "NULL"
            fare = f"{row['fare']:.4f}" if pd.notnull(row['fare']) else "NULL"
            
            # Boolean values
            adult_male = 'TRUE' if row['adult_male'] else 'FALSE'
            alone = 'TRUE' if row['alone'] else 'FALSE'
            
            row_sql = f"({row['survived']}, {row['pclass']}, {age}, {row['sibsp']}, {row['parch']}, {fare}, {adult_male}, {alone}, {sex_id}, {embarked_id}, {class_id}, {who_id}, {deck_id}, {embark_town_id}, {alive_id})"
            rows.append(row_sql)
        
        # Add rows in batches
        batch_size = 50
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            sql_content += "\n" + ",\n".join(batch)
            
            if i + batch_size < len(rows):
                sql_content += ";\n\nINSERT INTO Observation (survived, pclass, age, sibsp, parch, fare, adult_male, alone, sex_id, embarked_id, class_id, who_id, deck_id, embark_town_id, alive_id) VALUES"
            else:
                sql_content += ";\n"
        
        # Add final statements
        sql_content += f"""
-- Reset sequences
SELECT setval('observation_id_seq', {len(df)} + 1, false);

-- Update statistics
ANALYZE Sex;
ANALYZE Embarked;
ANALYZE Class;
ANALYZE Who;
ANALYZE Deck;
ANALYZE EmbarkTown;
ANALYZE Alive;
ANALYZE Observation;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Titanic database successfully initialized!';
    RAISE NOTICE '% passenger records loaded', (SELECT COUNT(*) FROM Observation);
END $$;
"""
        
        # Write the file
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        
        file_size = Path(output_file).stat().st_size / 1024
        print(f"SUCCESS: Generated {output_file} ({file_size:.1f} KB)")
        print(f"Records processed: {len(df)}")
        print("PostgreSQL init script ready!")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
