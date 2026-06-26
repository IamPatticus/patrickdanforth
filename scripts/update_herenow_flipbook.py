#!/usr/bin/env python3
"""
Update the Reginald flipbook on here.now
"""
import os
import json
import requests

API_BASE = "https://here.now/api/v1"
TOKEN = "75ac1fd0e3a5ace843a6aea3a7bc49c7f3144f1a032ee4807e5530340f0f8d4c"
SLUG = "grassy-canyon-yzmk"

def update_flipbook():
    archive_dir = os.path.expanduser("~/.cache/reginald-daily/archive")
    flipbook_dir = os.path.expanduser("/home/patrick/.openclaw/workspace/services/reginald-flipbook")
    
    # Get all images from archive
    images = []
    for f in sorted(os.listdir(archive_dir)):
        if f.startswith("reginald-") and f.endswith(".png"):
            date = f.replace("reginald-", "").replace(".png", "")
            images.append({
                "date": date,
                "filename": f,
                "label": f"Reginald — {date}"
            })
    
    # Create index.json
    index_data = {
        "count": len(images),
        "entries": images
    }
    index_json = json.dumps(index_data)
    
    # Read index.html
    with open(os.path.join(flipbook_dir, "index.html"), "r") as f:
        index_html = f.read()
    
    # Get files info for the publish
    files = []
    
    # Add index.html (this is the main page)
    files.append({
        "path": "index.html",
        "size": len(index_html.encode('utf-8')),
        "contentType": "text/html; charset=utf-8"
    })
    
    # Add index.json (for the JavaScript to read)
    files.append({
        "path": "index.json",
        "size": len(index_json.encode('utf-8')),
        "contentType": "application/json; charset=utf-8"
    })
    
    # Add all images
    for img in images:
        img_path = os.path.join(archive_dir, img["filename"])
        size = os.path.getsize(img_path)
        files.append({
            "path": f"images/{img['filename']}",
            "size": size,
            "contentType": "image/png"
        })
    
    # Step 1: Request update
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"Updating {SLUG} with {len(images)} images...")
    
    resp = requests.put(f"{API_BASE}/publish/{SLUG}", headers=headers, json={"files": files})
    if resp.status_code != 200:
        print(f"Failed to request update: {resp.status_code} - {resp.text}")
        return False
    
    result = resp.json()
    upload_info = result["upload"]
    uploads = upload_info["uploads"]
    
    # Step 2: Upload files
    for upload in uploads:
        path = upload["path"]
        url = upload["url"]
        content_type = upload["headers"]["Content-Type"]
        
        if path == "index.json":
            data = index_json.encode('utf-8')
        elif path == "index.html":
            data = index_html.encode('utf-8')
        else:
            # Extract filename from path (images/reginald-YYYY-MM-DD.png)
            filename = os.path.basename(path)
            img_path = os.path.join(archive_dir, filename)
            with open(img_path, 'rb') as f:
                data = f.read()
        
        upload_resp = requests.put(url, data=data, headers={"Content-Type": content_type})
        if upload_resp.status_code not in [200, 201]:
            print(f"Failed to upload {path}: {upload_resp.status_code}")
            return False
        print(f"Uploaded {path}")
    
    # Step 3: Finalize
    finalize_url = upload_info["finalizeUrl"]
    version_id = upload_info["versionId"]
    
    finalize_resp = requests.post(finalize_url, headers=headers, json={"versionId": version_id})
    if finalize_resp.status_code != 200:
        print(f"Failed to finalize: {finalize_resp.status_code} - {finalize_resp.text}")
        return False
    
    final = finalize_resp.json()
    print(f"✅ Flipbook updated!")
    print(f"   URL: {final.get('siteUrl', result.get('siteUrl', ''))}")
    print(f"   Images: {len(images)}")
    print(f"   Latest: {images[-1]['date']}")
    
    return True

if __name__ == "__main__":
    update_flipbook()
