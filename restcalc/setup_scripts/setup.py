from setup_db_sqlalchemy import main
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Set up the database with an admin user and operations in DB. Useful for testing and development purposes."
    )

    parser.add_argument(
        "--database-uri",
        type=str,
        default="postgresql://postgres:password@localhost:5432/postgres",
        help="Database URI to connect to. Default: postgresql://postgres:password@localhost:5432/postgres",
    )

    parser.add_argument(
        "--teardown",
        required=False,
        action="store_true",
    )

    parser.add_argument(
        "--is-docker",
        required=False,
        action="store_true",
        help="Use this flag if running in a Docker container.",
    )

    args = parser.parse_args()

    if args.is_docker:
        args.database_uri = args.database_uri.replace(
            "@localhost", "@postgres")

    main(args)
