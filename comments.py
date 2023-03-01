import requests
import os


def _get_nested_keys_in_json(json_data, nested_keys, default_value):
    json_subset = json_data

    for key in nested_keys:
        if key not in json_subset:
            return default_value
        else:
            json_subset = json_subset[key]

    return json_subset

def parse_docket_id(item_id):
    if item_id is None:
        return "unknown"

    segments = item_id.split('-') # list of segments separated by '-'
    segments_excluding_end = segments[:-1] # drops the last segment
    parsed_docket_id = '-'.join(segments_excluding_end)
    print(f'No DocketId Key found, parsing the "id" key')
    print(f'Id = {item_id}, Parsed DocketId = {parsed_docket_id}')
    return parsed_docket_id


def get_attributes(json_data, is_docket_json=False):
    '''
    Returns the agency, docket id, and item id from a loaded json object.
    '''
    item_id = _get_nested_keys_in_json(
        json_data, ['data', 'id'], None)
    agency_id = _get_nested_keys_in_json(
        json_data, ['data', 'attributes', 'agencyId'], None)

    if is_docket_json:
        docket_id = item_id
        item_id = None
    else:
        docket_id = _get_nested_keys_in_json(
            json_data, ['data', 'attributes', 'docketId'], None)

        if docket_id is None:
            docket_id = parse_docket_id(item_id)
            print(f'{item_id} was parsed to get docket id: {docket_id}.')

    # convert None value to respective folder names
    if not is_docket_json and item_id is None:
        item_id = 'unknown'
    if docket_id is None:
        docket_id = 'unknown'
    if agency_id is None:
        agency_id = 'unknown'

    return agency_id, docket_id, item_id

def get_comment_json_path(json):
    agencyId, docket_id, item_id = get_attributes(json)
    return f'data/{agencyId}/{docket_id}/text-{docket_id}/comments/{item_id}.json'


def get_attachment_json_paths(json):
    '''
    Given a json, this function will return all attachment paths for 
    n number attachment links
    '''
    agencyId, docket_id, item_id = get_attributes(json)

    # contains list of paths for attachments
    attachments = []

    # handles the case if "fileFormats" does not exist
    if ("fileFormats" not in json["included"][0]["attributes"]):
        print("This json is missing fileFormats")
        return attachments

    for attachment in json["included"][0]["attributes"]["fileFormats"]:
        if ("fileUrl" not in attachment):
            print("attachment download link does not exist for this attachment")
            continue

        attachment_name = attachment['fileUrl'].split("/")[-1]
        attachment_id = item_id + "_" + attachment_name
        attachments.append(f'data/{agencyId}/{docket_id}/binary-{docket_id}/comments_attachments/{attachment_id}')

    return attachments


# END OF PATH GENERATOR # END OF PATH GENERATOR # END OF PATH GENERATOR # END OF PATH GENERATOR # END OF PATH GENERATOR
# END OF PATH GENERATOR # END OF PATH GENERATOR # END OF PATH GENERATOR # END OF PATH GENERATOR # END OF PATH GENERATOR
# END OF PATH GENERATOR # END OF PATH GENERATOR # END OF PATH GENERATOR # END OF PATH GENERATOR # END OF PATH GENERATOR


# MAKE SURE TO YOUR ADD API KEY HERE !!!!
# MAKE SURE TO YOUR ADD API KEY HERE !!!!
# MAKE SURE TO YOUR ADD API KEY HERE !!!!
api_key = ''
comment_endpoint = "https://api.regulations.gov/v4/comments/USTR-2015-0010-0005"
response = requests.get(comment_endpoint + "?include=attachments&api_key=" + api_key)
json_response = response.json()


# makes a directory for a file 
def makeDirectory(filepath):
    '''
    Makes a path for a comment/attachment if one does not already exist
    '''
    filepath_components = filepath.split("/")
    filepath = "/".join(filepath_components[0:-1])
    try:
        os.makedirs(filepath)
    except FileExistsError:
        pass


def download_comment_json(json):
    '''
    Downloads the comment json and puts it in its correct path 
    '''
    file_path = get_comment_json_path(json)
    makeDirectory(file_path)
    with open(file_path, "wb") as file:
        file.write(response.content)
        file.close()


def download_attachments(json):
    '''
    Downloads all attachments for a comment
    '''
    # list of paths for attachmennts
    path_list = get_attachment_json_paths(json)
    for i, attachment in enumerate(json['included'][0]['attributes']['fileFormats']):
        url = attachment['fileUrl']
        download_single_attachment(url, path_list[i])


def download_single_attachment(url, path):
    '''
    Downloads a single attachment for a comment and writes it to its correct path
    '''
    response = requests.get(url)
    print(f"wrote {url} to path: " + path)
    makeDirectory(path)
    with open(path, "wb") as file:
        file.write(response.content)
        file.close()


# Execute - json_response is the json returned from API call to comment endpoint
download_attachments(json_response)
download_comment_json(json_response)