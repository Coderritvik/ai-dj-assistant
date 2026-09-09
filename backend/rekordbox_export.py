import os
from xml.etree.ElementTree import Element, SubElement, ElementTree

LIBRARY_DIR = "library"

def generate_rekordbox_xml(ordered_tracks, playlist_name="Generated Set"):
    root = Element("DJ_PLAYLISTS", Version="1.0.0")

    product = SubElement(root, "PRODUCT", Name="AI DJ Assistant", Version="1.0", Company="Custom")

    collection = SubElement(root, "COLLECTION", Entries=str(len(ordered_tracks)))

    for track in ordered_tracks:
        full_path = os.path.abspath(os.path.join(LIBRARY_DIR, track["filename"]))
        location_uri = "file://localhost" + full_path.replace(" ", "%20")

        SubElement(collection, "TRACK",
            TrackID=str(track["id"]),
            Name=track["filename"],
            Artist="",
            Tonality=track.get("camelot", ""),
            AverageBpm=str(track["bpm"]),
            Location=location_uri
        )

    playlists = SubElement(root, "PLAYLISTS")
    root_node = SubElement(playlists, "NODE", Type="0", Name="ROOT", Count="1")
    playlist_node = SubElement(root_node, "NODE", Type="1", Name=playlist_name,
                                 KeyType="0", Entries=str(len(ordered_tracks)))

    for track in ordered_tracks:
        SubElement(playlist_node, "TRACK", Key=str(track["id"]))

    return root


def save_xml(root, output_path):
    tree = ElementTree(root)
    tree.write(output_path, encoding="UTF-8", xml_declaration=True)