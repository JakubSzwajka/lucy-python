from agents.services.google_drive_manager import GoogleDriveManager

if __name__ == "__main__":
    gd = GoogleDriveManager()
    files = gd.list_files()
    for file in files:
        print(file)
