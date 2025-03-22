import subprocess
from tqdm import tqdm  # Import tqdm for the loading bar
from colorama import Fore, Style
import os

class WordlistGenerator:
    def __init__(self, target, dev=False):
        """
        Initializes the WordlistGenerator with the target URL.
        """
        self.target = target
        self.home_dir = os.path.expanduser("~")
        self.wordlist_path = "./crimson/words/dir"
        self.ferox_output = "./De_Dup/ferox.txt"
        self.urls_output = "./De_Dup/urls.txt"
        self.temp_cewl_output = "./De_Dup/temp_cewl.txt"
        self.final_cewl_output = "./De_Dup/cewl.txt"
        self.dev = dev

    def remove_existing_files(self):
        """
        Removes the existing output files if they exist.
        """
        files_to_remove = [self.ferox_output, self.urls_output, self.temp_cewl_output, self.final_cewl_output]
        for file in files_to_remove:
            if os.path.exists(file):
                print(f"{Fore.YELLOW}[-] Removing existing file: {file}{Style.RESET_ALL}")
                os.remove(file)

    def run_cewl(self):
        """
        Runs feroxbuster and generates a wordlist using cewl for the target.
        """
        try:
            
            self.remove_existing_files()

            # Step 1: Run feroxbuster
            ferox_command = [
                "feroxbuster",
                "-eknr",
                "--wordlist", self.wordlist_path,
                "-u", self.target,
                "-o", self.ferox_output
            ]
            print(f"{Fore.BLUE}[+] Running feroxbuster on {self.target}...{Style.RESET_ALL}")
            if self.dev == False:
                subprocess.run(ferox_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            elif self.dev == True:
                subprocess.run(ferox_command, check=True)

            # Step 2: Process ferox.txt to extract URLs
            grep_command = (
                f"cat {self.ferox_output} | grep 200 | grep -v 'png\\|\\.js' | cut -d 'h' -f2-100 | sed 's/^/h/g' >> {self.urls_output}"
            )
            print(f"{Fore.BLUE}[+] Extracting URLs from ferox.txt...{Style.RESET_ALL}")
            subprocess.run(grep_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            # Step 3: Generate a wordlist using cewl for each URL
            with open(self.urls_output, "r") as urls_file:
                urls = urls_file.read().splitlines()
                print(f"{Fore.BLUE}[+] Running cewl on extracted URLs...{Style.RESET_ALL}")
                
                # Using tqdm for loading bar: Initialize progress bar with the total number of URLs
                with tqdm(total=len(urls), desc="Processing URLs", unit="URL") as pbar:
                    for url in urls:
                        if url.startswith("http://") or url.startswith("https://"):
                            cewl_command = f"cewl -d 5 {url} >> {self.temp_cewl_output}"
                            subprocess.run(cewl_command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        else:
                            print(f"{Fore.RED}[!] Skipping invalid URL: {url}{Style.RESET_ALL}")
                        
                        pbar.update(1)  # Update progress bar after processing each URL

            # Step 4: Sort and remove duplicates from the cewl output
            sort_command = f"sort -u {self.temp_cewl_output} >> {self.final_cewl_output} && rm {self.temp_cewl_output}"
            print(f"{Fore.GREEN}[+] Sorting and deduplicating cewl output...{Style.RESET_ALL}")
            subprocess.run(sort_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            print(f"{Fore.GREEN}[+] Feroxbuster cewl wordlist completed.{Style.RESET_ALL}")

        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[!] An error occurred while running a command: {e}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[!] Unexpected error: {e}{Style.RESET_ALL}")

