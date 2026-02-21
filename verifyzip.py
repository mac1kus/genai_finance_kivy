import zipfile
import os

zip_path = input("Enter zip file path (or press Enter for 'project.zip'): ").strip()
if not zip_path:
    zip_path = "project.zip"

output_dir = "verified_contents"
os.makedirs(output_dir, exist_ok=True)

with zipfile.ZipFile(zip_path, 'r') as z:
    for name in z.namelist():
        data = z.read(name)
        # Rename: add "1" before extension e.g. main.py -> main1.py
        base, ext = os.path.splitext(os.path.basename(name))
        if ext:
            new_name = f"{base}1{ext}"
        else:
            new_name = base + "1"
        out_path = os.path.join(output_dir, new_name)
        with open(out_path, 'wb') as f:
            f.write(data)
        print(f"✔ {name} → {new_name}  ({len(data)} bytes)")

print(f"\nAll files extracted to '{output_dir}/' folder.")