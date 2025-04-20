import os
import time
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import text
from sqlmodel import Field, Session, SQLModel, create_engine, select

DATABASE_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DATABASE_URL = f'postgresql://postgres:postgres@{DATABASE_HOST}:5432/challenge_db'
engine = create_engine(DATABASE_URL)


class Animals(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    height: float
    weight: float
    walks_on_n_legs: int
    has_wings: bool
    has_tail: bool
    animal_type: str
    timestamp: datetime = Field(default_factory=datetime.now)


def wait_for_postgres(retries: int = 10, delay: float = 2.0) -> None:
    """
    Waits for a PostgreSQL connection to become available.

    :param engine: SQLAlchemy engine connected to PostgreSQL.
    :param retries: Number of retry attempts.
    :param delay: Delay between retries in seconds.
    :raises RuntimeError: If connection fails after all retries.
    """
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text('SELECT 1'))
                print('✅ PostgreSQL is ready!')
                return
        except Exception as e:
            print(f'⏳ Attempt {attempt}/{retries} - PostgreSQL not ready: {e}')
            time.sleep(delay)
    raise RuntimeError('❌ PostgreSQL did not become ready in time.')


wait_for_postgres()
SQLModel.metadata.create_all(engine)


def is_postgres_online() -> bool:
    """
    Checks if the PostgreSQL server is reachable.

    :return: True if PostgreSQL is reachable, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        return True
    except Exception as e:
        print(f'Error connecting to PostgreSQL: {e}')
        return False


def insert_animals(animals: List[dict]) -> bool:
    """
    Insert a list of animal records into the database.

    :param animals: List of dicts with animal data.
    :return: True if insert succeeded, False otherwise.
    """
    try:
        with Session(engine) as session:
            for result in animals:
                sql_animal = Animals(**result)
                session.add(sql_animal)
            session.commit()
            return True
    except Exception:
        return False


def get_animals_between(start: datetime, end: datetime) -> List[dict]:
    """
    Retrieve animal records stored between two datetime values.

    :param start: Start datetime (inclusive).
    :param end: End datetime (inclusive).
    :return: List of animal records as dictionaries.
    :raises ValueError: If there is an error retrieving data from the database.
    """
    try:
        with Session(engine) as session:
            statement = select(Animals).where(Animals.timestamp.between(start, end))
            results = session.exec(statement).all()
            return [animal.model_dump() for animal in results]
    except Exception:
        raise ValueError('Error retrieving data from the database.')


if __name__ == '__main__':
    print('Is postgres Online?:', is_postgres_online())

    # Insert example data
    animals_data = [
        {'height': 1.2, 'weight': 30.5, 'walks_on_n_legs': 4, 'has_wings': False, 'has_tail': True},
        {'height': 0.5, 'weight': 5.0, 'walks_on_n_legs': 2, 'has_wings': True, 'has_tail': False},
    ]
    print('Animal data insert OK?:', insert_animals(animals_data))

    # Retrieve data between two timestamps
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now()
    animals = get_animals_between(start_time, end_time)
    print(animals)
