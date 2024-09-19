import argparse
import os
import logging

from dotenv import load_dotenv
import psycopg2
import pandas as pd

from logreef.security import hash_password


logging.getLogger("passlib").setLevel(logging.ERROR)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def import_to_db(username, email, password, aquarium_name, filepath, is_demo: bool = False):
    conn = psycopg2.connect(os.getenv("DB_URL"))

    # create new user
    query = f"""
        INSERT INTO users (username, email, hash_password, verified, is_demo)
            VALUES ('{username}', '{email}', '{hash_password(password)}', {True}, {is_demo})
            RETURNING id
    """
    with conn.cursor() as cur:
        cur.execute(query)
        user_id = cur.fetchone()[0]
    conn.commit()

    # create Default aquarium
    query = f"""
        INSERT INTO aquariums (user_id, name)
            VALUES ({user_id}, '{aquarium_name}')
            RETURNING id
    """
    with conn.cursor() as cur:
        cur.execute(query)
        aquarium_id = cur.fetchone()[0]
    conn.commit()

    tmp_file_path = "temp.csv"
    # process file to import
    df = pd.read_csv(filepath).drop("id", axis=1)
    df.user_id = user_id
    df.aquarium_id = aquarium_id
    df.to_csv(tmp_file_path, index=False, header=False)

    # copy file to db
    with conn.cursor() as cur:
        with open(tmp_file_path, "r") as f:
            cur.copy_from(
                f,
                "param_values",
                sep=",",
                columns=[
                    "user_id",
                    "aquarium_id",
                    "param_type_name",
                    "test_kit_name",
                    "value",
                    "timestamp",
                    "note",
                    "created_on",
                    "updated_on",
                ],
            )
    conn.commit()
    conn.close()

    # cleaup
    os.remove(tmp_file_path)

    logger.info(f"{filepath} imported succesfully to username {username}")


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="test", type=str)
    parser.add_argument("--email", default="test@thereeflog.com", type=str)
    parser.add_argument("--password", default="testtest", type=str)
    parser.add_argument("--file", default="test.csv", type=str)
    parser.add_argument("--demo", action="store_true")


    args = parser.parse_args()

    import_to_db(args.username, args.email, args.password, "Default", args.file, is_demo=args.demo)
