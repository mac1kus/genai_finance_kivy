import zipfile
import os

def create_project_zip():
    # These are the 3 files you need for the APK build
    files_to_zip = ['main.py', 'aria.kv', 'buildozer.spec']
    zip_name = 'project.zip'

    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files_to_zip:
                if os.path.exists(file):
                    zipf.write(file)
                    print(f"Added {file} to {zip_name}")
                else:
                    print(f"ERROR: {file} not found in this folder!")
        
        if os.path.exists(zip_name):
            print(f"\nSUCCESS: {zip_name} is created and ready for Colab.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_project_zip()