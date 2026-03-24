#!/usr/bin/env python3
import re
import urllib.parse
import subprocess
import json
import sys
import concurrent.futures
from datetime import datetime

# Extract all tags from index.html
with open('index.html', 'r') as f:
    content = f.read()

# Find the SAP_TAGS array
match = re.search(r'const SAP_TAGS = \[(.*?)\];', content, re.DOTALL)
if not match:
    print("Could not find SAP_TAGS array")
    sys.exit(1)

# Extract tag names from the array
tags_str = match.group(1)
tags = re.findall(r'"([^"]+)"', tags_str)

# Filter to only get actual tag names (not category info)
tags = [t.strip() for t in tags if t.strip() and not t.startswith('cat:')]
tags = sorted(set(tags))  # Remove duplicates and sort

print(f"Found {len(tags)} total tags to test")
print(f"Testing tags against accurate-feed RSS endpoint using parallel requests...")
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

failing_tags = []
success_count = 0
error_count = 0

def test_tag(tag):
    """Test a single tag against the API"""
    encoded_tag = urllib.parse.quote(tag)
    url = f"https://rss-scn.marianzeis.de/api/messages?conversation.style=blog&managedTag.title={encoded_tag}&feeds.replies=false"

    try:
        result = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', url],
                              capture_output=True, text=True, timeout=10)
        http_code = result.stdout.strip()
        return {'tag': tag, 'code': http_code, 'success': True}
    except Exception as e:
        return {'tag': tag, 'error': str(e), 'success': False}

# Use ThreadPoolExecutor for parallel requests (10 concurrent)
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(test_tag, tag) for tag in tags]

    for idx, future in enumerate(concurrent.futures.as_completed(futures), 1):
        result = future.result()
        tag = result['tag']

        if result['success']:
            http_code = result['code']
            if http_code == '400':
                failing_tags.append(tag)
                error_count += 1
                print(f"[{idx}/{len(tags)}] FAIL (HTTP 400): {tag}")
            elif http_code == '200':
                success_count += 1
                if idx % 20 == 0:
                    print(f"[{idx}/{len(tags)}] Progress: {success_count} successful, {error_count} failed")
            else:
                print(f"[{idx}/{len(tags)}] WARNING (HTTP {http_code}): {tag}")
        else:
            print(f"[{idx}/{len(tags)}] ERROR testing {tag}: {result.get('error', 'Unknown error')}")

print("=" * 60)
print(f"\nTest Summary:")
print(f"Total tags tested: {len(tags)}")
print(f"Successful: {success_count}")
print(f"Failed (HTTP 400): {error_count}")
print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

print(f"\n--- FAILING TAGS ({len(failing_tags)} total) ---")
for tag in sorted(failing_tags):
    print(f"  - {tag}")

# Save results to file for reference
with open('test_results.json', 'w') as f:
    json.dump({
        'failing_tags': sorted(failing_tags),
        'total_tested': len(tags),
        'total_failed': len(failing_tags),
        'total_successful': success_count
    }, f, indent=2)
