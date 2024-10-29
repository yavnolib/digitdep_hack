from src.db_iface import PostgreIface
from src.addr_processor import AddrParser
import argparse
import os
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description="Parser for mode and path.")
    parser.add_argument(
        "--mode",
        type=int,
        default=0,
        choices=[0, 1, 2],
        help="Operating mode ([0, 1, 2]). Default is 0."
    )
    parser.add_argument(
        "--cache_folder",
        type=str,
        default='/mnt/cache',
        help="Path to the file. Default is '/mnt/cache'."
    )
    parser.add_argument(
        "--buyer_path",
        type=str,
        default='/mnt/buyer.xlsx',
        help="Path to the file. Default is '/mnt/buyer.xlsx'."
    )

    args = parser.parse_args()

    if (args.mode in [1, 2]) and not os.path.isfile(args.buyer_path):
        print(f"Error: File '{args.buyer_path}' does not exist.")
        sys.exit(1)
    return args

if __name__ == '__main__':
    """
    Examples of usage.

    a) Init database:
    ```
    python3 db_controller.py --mode 0 --cache_folder /mnt/cache
    ```

    b) Update `buyer` table from file /mnt/buyer.xlsx WITHOUT coordinates:
    ```
    python3 db_controller.py --mode 1 --buyer_path /mnt/buyer.xlsx
    ```

    c) Update `buyer` table from file /mnt/buyer.xlsx WITH coordinates:
    ```
    python3 db_controller.py --mode 2 --buyer_path /mnt/buyer.xlsx
    ```
    Attention! 
    CSV MUST BE IN FORMAT:
    ```
    code, addr, geo
    1234,"Адрес","100.0,110.0"
    ```
    where coordinates follow in the format: "<degrees NORTH latitude>,<degrees EAST longitude>
    """
    args = parse_arguments()
    mode = args.mode

    if mode == 0:
        """ Initialise necessary tables in database """
        
        postgre = PostgreIface()
        postgre.create_database(path_to_cache=args.cache_folder)

    elif mode == 1:
        """ Update `buyer` table with values ​​from new `Справочник грузополучателей.xlsx` table using parser """

        file_to_process = args.buyer_path
        parser = AddrParser(file_to_process=file_to_process)
        df = parser.process()
    
    elif mode == 2:
        """ Update `buyer` table with values ​​from new `Справочник грузополучателей.xlsx` table WITHOUT PARSING """
        file_to_process = args.buyer_path
        postgre = PostgreIface()
        postgre.upd_buyers_mode_2(file_to_process)
        