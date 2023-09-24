import os
import hashlib
import re


class Scanner:
    def __init__(self, signature_database_directory):
        self.virus_db = self.load_signatures_database(
            signature_database_directory)

    def load_signatures_database(self, db_dir):
        signatures = set()
        for root, _, files in os.walk(db_dir):
            for file_name in files:
                with open(os.path.join(root, file_name), 'rb') as file:
                    signatures.add(hashlib.md5(file.read()).hexdigest())
        return signatures

    def scan_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                content = file.read()

                # Find known virus signatures
                file_hash = hashlib.md5(content).hexdigest()
                if file_hash in self.virus_db:
                    print(f"File {file_path} is infected (Known Signature).")
                    return True

                # Check for common malware patterns using regular expressions
                common_patterns = [r'malware_pattern_1', r'malware_pattern_2']
                for pattern in common_patterns:
                    if re.search(pattern, content.decode('utf-8', errors='ignore')):
                        print(
                            f"File {file_path} is infected (Pattern: {pattern}).")
                        return True

            print(f"File {file_path} is clean.")
            return False
        except Exception as e:
            print(f"Error scanning {file_path}: {str(e)}")
            return False

    def scan_directory(self, dir_path):
        if not os.path.isdir(dir_path):
            print(f"{dir_path} is not a valid directory.")
            return

        for root, _, files in os.walk(dir_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                self.scan_file(file_path)


if __name__ == "__main__":
    virus_db_directory = "/path/to/virus_database"
    scanner = Scanner(virus_db_directory)
    directory_to_scan = "/path/to/scan"

    print(f"Scanning directory: {directory_to_scan}")
    scanner.scan_directory(directory_to_scan)
