#!/usr/bin/env python3
"""Search and download sound effects from Freesound.org API."""

import urllib.request
import urllib.parse
import json
import sys
import os

FREESOUND_API_URL = "https://freesound.org/apiv2"

def search(query, token, max_results=10, duration_max=5.0, fields="id,name,previews,duration,license,username"):
    """Search Freesound for sound effects matching query."""
    params = urllib.parse.urlencode({
        "query": query,
        "fields": fields,
        "filter": f"duration:[0 TO {duration_max}]" if duration_max else "",
        "sort": "rating_desc",
        "page_size": max_results,
        "token": token,
    })
    url = f"{FREESOUND_API_URL}/search/text/?{params}"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    results = data.get("results", [])
    for i, r in enumerate(results):
        print(f"  [{i+1}] {r['name']} ({r['duration']:.1f}s) by {r['username']} | License: {r['license']} | ID: {r['id']}")
    return results

def download_preview(sound_id, token, output_dir="."):
    """Download the preview MP3 for a sound (no OAuth needed)."""
    # First get the sound info to find the preview URL
    url = f"{FREESOUND_API_URL}/sounds/{sound_id}/?fields=previews,name&token={token}"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    preview_url = data["previews"]["preview-hq-mp3"]
    name = data["name"].replace(" ", "_").replace("/", "_")
    filename = os.path.join(output_dir, f"{name}.mp3")
    urllib.request.urlretrieve(preview_url, filename)
    print(f"Downloaded: {filename}")
    return filename

def main():
    if len(sys.argv) < 3:
        print("Usage: python freesound_search.py <command> <token> [args]")
        print("Commands:")
        print("  search <token> <query> [max_results] [max_duration]")
        print("  download <token> <sound_id> [output_dir]")
        sys.exit(1)

    command = sys.argv[1]
    token = sys.argv[2]

    if command == "search":
        query = sys.argv[3] if len(sys.argv) > 3 else "whoosh"
        max_results = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        max_duration = float(sys.argv[5]) if len(sys.argv) > 5 else 5.0
        print(f"Searching: '{query}' (max {max_results} results, max {max_duration}s)")
        search(query, token, max_results, max_duration)
    elif command == "download":
        sound_id = sys.argv[3]
        output_dir = sys.argv[4] if len(sys.argv) > 4 else "."
        os.makedirs(output_dir, exist_ok=True)
        download_preview(sound_id, token, output_dir)
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
