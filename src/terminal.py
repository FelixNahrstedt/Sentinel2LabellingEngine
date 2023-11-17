import re
from modules.OverpassQuery import query_OSM

def validate_date_format(date_str):
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    return re.match(date_pattern, date_str)

def get_data(name: str, node_size: int, scaling_factor: int, use_sentinel_1: bool, use_sentinel_2: bool,
             query: str, start_date: str, end_date: str):
    """
    Get data based on specified parameters.
    
    Args:
        name (str): Name for the request.
        node_size (int): Size of the physical element to observe.
        scaling_factor (int): Buffer size around the images.
        use_sentinel_1 (bool): Specify if Sentinel-1 data is used.
        use_sentinel_2 (bool): Specify if Sentinel-2 data is used.
        query (str): Overpass turbo / OSM API query for nodes.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
    """
    if not validate_date_format(start_date) or not validate_date_format(end_date):
        print("Start or end date does not match the 'YYYY-MM-DD' format.")
        return
    
    buffer_size = node_size * scaling_factor
    satellite_name = "Sentinel-2"
    if not use_sentinel_1 and not use_sentinel_2:
        print("No satellite specified.")
        return
    elif use_sentinel_1 and use_sentinel_2:
        satellite_name = "Sentinel-1 and Sentinel-2"
    elif use_sentinel_1:
        satellite_name = "Sentinel-1"
    
    node_len = query_OSM(query, buffer_size, name)
    print(f"You selected {node_len} nodes from Overpass API.\n"
          f"Do you want to download the respective {satellite_name} images?")

#def download_images():
    
# Example query
query = '''[out:json];
    area["ISO3166-1"="NL"];
    (node["power"="generator"]["generator:source"="wind"]["manufacturer"="Vestas"](area);
    );
    out center;'''

# Example function call
get_data("WindVestasNL", 1000, 10, use_sentinel_1=False, use_sentinel_2=True, query=query,
         start_date="2021-01-01", end_date="2021-02-01")
