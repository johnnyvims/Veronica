import subprocess
import os
from colorama import Fore, Style
import re
import sys
from collections import defaultdict

class DiectoryAutomation:
    def __init__(self, url, wordlist_dir="./De_Dup", extensions='.txt', dev=False):
        """
        Initializes the FfufAutomation class with the target URL and wordlist directory.
        """
        self.url = url
        self.wordlist_dir = wordlist_dir
        self.extensions = extensions
        self.results = []
        self.dev = dev

    def run_dirsearch(self):
        # Build the command
        print("\n")
        print(Fore.BLUE + "--- DIRSEARCH ---" + Style.RESET_ALL)
        print("\n")
        command = [
            "dirsearch",
            "-u", self.url,
            "-t", "20",
            "-i", "200"
        ]

        # Run the command using subprocess
        subprocess.run(command, check=True)
        print("\n")


    def find_extension(self):
        try:
            result = subprocess.run(
                [
                    "ffuf",
                    "-w", "./De_Dup/web-extensions.txt:FUZZ",
                    "-u", f"{self.url.rstrip('/')}/indexFUZZ"
                ],
                capture_output=True, text=True, check=True
            )

            output = result.stdout
            print(f"{Fore.BLUE}extension output:{Style.RESET_ALL}")
            for line in output.splitlines():  # Split the output by lines
                print(f"{Fore.BLUE}{line}{Style.RESET_ALL}")
            matches = re.findall(r"(\.\w+)\s+\[Status:\s*(200|301|302)", output)

            if matches:
            #    self.extensions = ",".join(sorted(set(match[0] for match in matches)))
            #    print(f"Detected extension: {self.extension}")
                detected_extensions = {match[0] for match in matches}
                detected_extensions.add('.txt')  # Ensuring .txt is always included
                self.extensions = ",".join(sorted(detected_extensions))
                print(f"{Fore.GREEN}[+] Detected extensions: {self.extensions}{Style.RESET_ALL}")
            else:
                self.extensions = ".txt.php"
                print(f"{Fore.BLUE}[-] No valid extensions found. applying common linux extensions: {self.extensions}")

        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[!]Error running FFUF: {e}{Style.RESET_ALL}")


    def extract_ffuf_results(self, output):
        """
        Extracts relevant details (size, words, lines) from the ffuf output.
        Returns a list of tuples containing size, words, and lines.
        """
        results = []
        regex = r"Size:\s*(\d+).*Words:\s*(\d+).*Lines:\s*(\d+)"
        for line in output.splitlines():
            match = re.search(regex, line)
            if match:
                size = match.group(1)
                words = match.group(2)
                lines = match.group(3)
                results.append((size, words, lines))
        return results

    def run_ffuf_test(self, wordlist):
        """
        Runs ffuf with the specified parameters and returns the output.
        """
        try:
            ffuf_command = [
                "ffuf",
                "-w", wordlist,
                "-u", f"{self.url}/FUZZ",
                "-e", self.extensions,
                "-c"
            ]
            print(f"{Fore.GREEN}[+] running ffuf test to get filters{Style.RESET_ALL}")
            #subprocess.run(ffuf_command, check=True)    #verbose mode could include this
            result = subprocess.run(ffuf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return result.stdout.decode()

        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[!] Error running ffuf: {e}{Style.RESET_ALL}")
            return None

    def run_ffuf_size(self, size_filter):
        """
        Runs ffuf with various wordlists and applies the size filter.
        """
        print(f"{Fore.BLUE}[-] running ffuf with size filter{Style.RESET_ALL}")
        if self.dev == False:
            new_wordlist = [
                "default-web-root-directory-windows.txt", "common_directories.txt", "default-web-root-directory-linux.txt", "Randomfiles.fuzz.txt", "rssfeed-files.txt",
                "UnixDotfiles.fuzz.txt", "Passwords.fuzz.txt", "ntlm-directories.txt", "domino-dirs-coldfusion39.txt", "versioning_metafiles.txt", "raft-medium-files.txt",
                "Oracle-EBS-wordlist.txt", "combined_words.txt", "raft-small-files.txt", "raft-medium-words.txt", "raft-medium-directories.txt", "dsstorewordlist.txt",
                "raft-small-words.txt", "raft-small-directories.txt", "raft-large-files.txt", "raft-large-directories.txt", "raft-large-words.txt", "raft-medium-files-lowercase.txt",
                "directory-list-2.3-small.txt", "raft-medium-directories-lowercase.txt", "raft-medium-words-lowercase.txt", "raft-small-files-lowercase.txt", "dirsearch.txt",
                "raft-small-words-lowercase.txt", "raft-small-directories-lowercase.txt", "directory-list-2.3-medium.txt", "raft-large-files-lowercase.txt", "raft-large-directories-lowercase.txt",
                "raft-large-words-lowercase.txt", "directory-list-lowercase-2.3-small.txt", "directory-list-lowercase-2.3-medium.txt", "directory-list-1.0.txt", "directory-list-2.3-big.txt",
                "directory-list-lowercase-2.3-big.txt"
                ]
        elif self.dev == True:
            new_wordlist= ["Randomfiles.fuzz.txt"]

        valid_wordlists = [os.path.join(self.wordlist_dir, wordlist) for wordlist in new_wordlist if os.path.isfile(os.path.join(self.wordlist_dir, wordlist))]
        if not valid_wordlists:
            print(f"{Fore.RED}[!] No valid wordlists found.{Style.RESET_ALL}")
            return

        cewl_path = os.path.join("./De_Dup", "cewl.txt")

        if os.path.exists(cewl_path):
            valid_wordlists.append(cewl_path)
            print(f"{Fore.GREEN}[+] adding cewl.txt to enumration Congrats! {Style.RESET_ALL}")


        # List to capture outputs from all iterations
        all_outputs = []

        for wordlist in valid_wordlists:
            print(f"{Fore.CYAN}[+] Running ffuf with wordlist: {wordlist}{Style.RESET_ALL}")
            ffuf_command = [
                "ffuf",
                "-w", wordlist,
                "-u", f"{self.url}/FUZZ",
                "-e", self.extensions,
                "-fs", size_filter,  # Apply the size filter here
                "-c"
            ]
        
            try:
                # Run the ffuf command and capture the output
                #subprocess.run(ffuf_command, check=True)      #verbose mode could include this
                result = subprocess.run(ffuf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                all_outputs.append(result.stdout.decode())
            except subprocess.CalledProcessError as e:
                print(f"{Fore.RED}[!] Error running ffuf with wordlist {wordlist}: {e}{Style.RESET_ALL}")

        self.process_ffuf_results(all_outputs)


##        # Process the captured outputs after all iterations
##        print(f"{Fore.YELLOW}[+] Processed {len(all_outputs)} outputs from all wordlists.{Style.RESET_ALL}")
##        # You can now iterate over `all_outputs` to analyze each one
##        for i, output in enumerate(all_outputs):
##            if i == 0:
##                print(f"{Fore.CYAN}\n--- Output from FFUF ---\n{Style.RESET_ALL}")
##            if output.strip():
##                #print(f"{Fore.GREEN}[+] Output from wordlist {valid_wordlists[i]}:{Style.RESET_ALL}")
##                print(output)
##            else:
##                pass

    
    def run_ffuf_word(self, word_filter):
        """
        Runs ffuf with various wordlists and applies the size filter.
        """
        print(f"{Fore.BLUE}[-] running ffuf with word filter{Style.RESET_ALL}")

        if self.dev == False:
            new_wordlist = [
                "default-web-root-directory-windows.txt", "common_directories.txt", "default-web-root-directory-linux.txt", "Randomfiles.fuzz.txt", "rssfeed-files.txt",
                "UnixDotfiles.fuzz.txt", "Passwords.fuzz.txt", "ntlm-directories.txt", "domino-dirs-coldfusion39.txt", "versioning_metafiles.txt", "raft-medium-files.txt",
                "Oracle-EBS-wordlist.txt", "combined_words.txt", "raft-small-files.txt", "raft-medium-words.txt", "raft-medium-directories.txt", "dsstorewordlist.txt",
                "raft-small-words.txt", "raft-small-directories.txt", "raft-large-files.txt", "raft-large-directories.txt", "raft-large-words.txt", "raft-medium-files-lowercase.txt",
                "directory-list-2.3-small.txt", "raft-medium-directories-lowercase.txt", "raft-medium-words-lowercase.txt", "raft-small-files-lowercase.txt", "dirsearch.txt",
                "raft-small-words-lowercase.txt", "raft-small-directories-lowercase.txt", "directory-list-2.3-medium.txt", "raft-large-files-lowercase.txt", "raft-large-directories-lowercase.txt",
                "raft-large-words-lowercase.txt", "directory-list-lowercase-2.3-small.txt", "directory-list-lowercase-2.3-medium.txt", "directory-list-1.0.txt", "directory-list-2.3-big.txt",
                "directory-list-lowercase-2.3-big.txt"
                ]
        elif self.dev == True:
            new_wordlist= ["Randomfiles.fuzz.txt"]


        valid_wordlists = [os.path.join(self.wordlist_dir, wordlist) for wordlist in new_wordlist if os.path.isfile(os.path.join(self.wordlist_dir, wordlist))]
        if not valid_wordlists:
            print(f"{Fore.RED}[!] No valid wordlists found.{Style.RESET_ALL}")
            return

        cewl_path = os.path.join("./De_Dup", "cewl.txt")

        if os.path.exists(cewl_path):
            valid_wordlists.append(cewl_path)
            print(f"{Fore.GREEN}[+] adding cewl.txt to enumration Congrats! {Style.RESET_ALL}")

        # List to capture outputs from all iterations
        all_outputs = []

        for wordlist in valid_wordlists:
            print(f"{Fore.CYAN}[+] Running ffuf with wordlist: {wordlist}{Style.RESET_ALL}")
            ffuf_command = [
                "ffuf",
                "-w", wordlist,
                "-u", f"{self.url}/FUZZ",
                "-e", self.extensions,
                "-fw", word_filter,  # Apply the size filter here
                "-c"
            ]
        
            try:
                # Run the ffuf command and capture the output
                #subprocess.run(ffuf_command, check=True)      #verbose mode could include this
                result = subprocess.run(ffuf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                all_outputs.append(result.stdout.decode())
            except subprocess.CalledProcessError as e:
                print(f"{Fore.RED}[!] Error running ffuf with wordlist {wordlist}: {e}{Style.RESET_ALL}")

        self.process_ffuf_results(all_outputs)

        # Process the captured outputs after all iterations
        ##print(f"{Fore.YELLOW}[+] Processed {len(all_outputs)} outputs from all wordlists.{Style.RESET_ALL}")
        # You can now iterate over `all_outputs` to analyze each one
        ##for i, output in enumerate(all_outputs):
        ##    if i == 0:
        ##        print(f"{Fore.CYAN}\n--- Output from FFUF ---\n{Style.RESET_ALL}")
        ##    if output.strip():
        ##        #print(f"{Fore.GREEN}[+] Output from wordlist {valid_wordlists[i]}:{Style.RESET_ALL}")
        ##        print(output)
        ##    else:
        ##        pass


    def run_ffuf_line(self, line_filter):
        """
        Runs ffuf with various wordlists and applies the size filter.
        """
        print(f"{Fore.BLUE}[-] running ffuf with line filter{Style.RESET_ALL}")
        if self.dev == False:
            new_wordlist = [
                "default-web-root-directory-windows.txt", "common_directories.txt", "default-web-root-directory-linux.txt", "Randomfiles.fuzz.txt", "rssfeed-files.txt",
                "UnixDotfiles.fuzz.txt", "Passwords.fuzz.txt", "ntlm-directories.txt", "domino-dirs-coldfusion39.txt", "versioning_metafiles.txt", "raft-medium-files.txt",
                "Oracle-EBS-wordlist.txt", "combined_words.txt", "raft-small-files.txt", "raft-medium-words.txt", "raft-medium-directories.txt", "dsstorewordlist.txt",
                "raft-small-words.txt", "raft-small-directories.txt", "raft-large-files.txt", "raft-large-directories.txt", "raft-large-words.txt", "raft-medium-files-lowercase.txt",
                "directory-list-2.3-small.txt", "raft-medium-directories-lowercase.txt", "raft-medium-words-lowercase.txt", "raft-small-files-lowercase.txt", "dirsearch.txt",
                "raft-small-words-lowercase.txt", "raft-small-directories-lowercase.txt", "directory-list-2.3-medium.txt", "raft-large-files-lowercase.txt", "raft-large-directories-lowercase.txt",
                "raft-large-words-lowercase.txt", "directory-list-lowercase-2.3-small.txt", "directory-list-lowercase-2.3-medium.txt", "directory-list-1.0.txt", "directory-list-2.3-big.txt",
                "directory-list-lowercase-2.3-big.txt"
                ]
        elif self.dev == True:
            new_wordlist= ["Randomfiles.fuzz.txt"]


        valid_wordlists = [os.path.join(self.wordlist_dir, wordlist) for wordlist in new_wordlist if os.path.isfile(os.path.join(self.wordlist_dir, wordlist))]
        if not valid_wordlists:
            print(f"{Fore.RED}[!] No valid wordlists found.{Style.RESET_ALL}")
            return

        cewl_path = os.path.join("./De_Dup", "cewl.txt")

        if os.path.exists(cewl_path):
            valid_wordlists.append(cewl_path)
            print(f"{Fore.GREEN}[+] adding cewl.txt to enumration Congrats! {Style.RESET_ALL}")


        # List to capture outputs from all iterations
        all_outputs = []

        for wordlist in valid_wordlists:
            print(f"{Fore.CYAN}[+] Running ffuf with wordlist: {wordlist}{Style.RESET_ALL}")
            ffuf_command = [
                "ffuf",
                "-w", wordlist,
                "-u", f"{self.url}/FUZZ",
                "-e", self.extensions,
                "-fl", line_filter,  # Apply the size filter here
                "-c"
            ]
        
            try:
                # Run the ffuf command and capture the output
                #subprocess.run(ffuf_command, check=True)      #verbose mode could include this
                result = subprocess.run(ffuf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                all_outputs.append(result.stdout.decode())
            except subprocess.CalledProcessError as e:
                print(f"{Fore.RED}[!] Error running ffuf with wordlist {wordlist}: {e}{Style.RESET_ALL}")
        
        self.process_ffuf_results(all_outputs)

##        # Process the captured outputs after all iterations
##        print(f"{Fore.YELLOW}[+] Processed {len(all_outputs)} outputs from all wordlists.{Style.RESET_ALL}")
##        # You can now iterate over `all_outputs` to analyze each one
##        for i, output in enumerate(all_outputs):
##            if i == 0:
##                print(f"{Fore.CYAN}\n--- Output from FFUF ---\n{Style.RESET_ALL}")
##            if output.strip():
##                #print(f"{Fore.GREEN}[+] Output from wordlist {valid_wordlists[i]}:{Style.RESET_ALL}")
##                
##                '''
##                instead of printing the results we need to store them into memory and remove duplicates and also start the search for login pages for exploit suggester and print it nicely instead so remove white spaces
##                '''
##
##                print(output)
##            else:
##                pass


    def run_ffuf_real_no_filter(self):
        """
        Runs ffuf with various wordlists and applies the size filter.
        """
        print(f"{Fore.BLUE}[-] running ffuf no filter{Style.RESET_ALL}")
        if self.dev == False:
            new_wordlist = [
                "default-web-root-directory-windows.txt", "common_directories.txt", "default-web-root-directory-linux.txt", "Randomfiles.fuzz.txt", "rssfeed-files.txt",
                "UnixDotfiles.fuzz.txt", "Passwords.fuzz.txt", "ntlm-directories.txt", "domino-dirs-coldfusion39.txt", "versioning_metafiles.txt", "raft-medium-files.txt",
                "Oracle-EBS-wordlist.txt", "combined_words.txt", "raft-small-files.txt", "raft-medium-words.txt", "raft-medium-directories.txt", "dsstorewordlist.txt",
                "raft-small-words.txt", "raft-small-directories.txt", "raft-large-files.txt", "raft-large-directories.txt", "raft-large-words.txt", "raft-medium-files-lowercase.txt",
                "directory-list-2.3-small.txt", "raft-medium-directories-lowercase.txt", "raft-medium-words-lowercase.txt", "raft-small-files-lowercase.txt", "dirsearch.txt",
                "raft-small-words-lowercase.txt", "raft-small-directories-lowercase.txt", "directory-list-2.3-medium.txt", "raft-large-files-lowercase.txt", "raft-large-directories-lowercase.txt",
                "raft-large-words-lowercase.txt", "directory-list-lowercase-2.3-small.txt", "directory-list-lowercase-2.3-medium.txt", "directory-list-1.0.txt", "directory-list-2.3-big.txt",
                "directory-list-lowercase-2.3-big.txt"
                ]
        elif self.dev == True:
            new_wordlist= ["Randomfiles.fuzz.txt"]

        valid_wordlists = [os.path.join(self.wordlist_dir, wordlist) for wordlist in new_wordlist if os.path.isfile(os.path.join(self.wordlist_dir, wordlist))]
        if not valid_wordlists:
            print(f"{Fore.RED}[!] No valid wordlists found.{Style.RESET_ALL}")
            return

        cewl_path = os.path.join("./De_Dup", "cewl.txt")

        if os.path.exists(cewl_path):
            valid_wordlists.append(cewl_path)
            print(f"{Fore.GREEN}[+] adding cewl.txt to enumration Congrats! {Style.RESET_ALL}")

        # List to capture outputs from all iterations
        all_outputs = []

        for wordlist in valid_wordlists:
            print(f"{Fore.CYAN}[+] Running ffuf with wordlist: {wordlist}{Style.RESET_ALL}")
            ffuf_command = [
                "ffuf",
                "-w", wordlist,
                "-u", f"{self.url}/FUZZ",
                "-e", self.extensions,
                "-c"
            ]
        
            try:
                # Run the ffuf command and capture the output
                #subprocess.run(ffuf_command, check=True)
                result = subprocess.run(ffuf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                all_outputs.append(result.stdout.decode())
            except subprocess.CalledProcessError as e:
                print(f"{Fore.RED}[!] Error running ffuf with wordlist {wordlist}: {e}{Style.RESET_ALL}")

        self.process_ffuf_results(all_outputs)


##        # Process the captured outputs after all iterations
##        print(f"{Fore.YELLOW}[+] Processed {len(all_outputs)} outputs from all wordlists.{Style.RESET_ALL}")
##        # You can now iterate over `all_outputs` to analyze each one
##        for i, output in enumerate(all_outputs):
##            if i == 0:
##                print(f"{Fore.CYAN}\n--- Output from FFUF ---\n{Style.RESET_ALL}")
##            if output.strip():
##                #print(f"{Fore.GREEN}[+] Output from wordlist {valid_wordlists[i]}:{Style.RESET_ALL}")
##                print(output)
##            else:
##                pass

    def analyze_results(self, output):
        """
        Analyzes the ffuf output and applies filtering logic based on repeating values in specific fields.
        """
        self.results = self.extract_ffuf_results(output)

        if len(self.results) > 1:
            first_field_repeats = all(result[0] == self.results[0][0] for result in self.results)
            second_field_repeats = all(result[1] == self.results[0][1] for result in self.results)
            third_field_repeats = all(result[2] == self.results[0][2] for result in self.results)

            print(f"result 0 0: {self.result[0][0]} should be size")
            print(f"result 0 1: {self.result[0][1]} should be word")
            print(f"result 0 2: {self.result[0][2]} should be line")
    
            print("result for loop incoming")
            for result in self.results:
                print(result)

            if first_field_repeats:
                size_filter = self.results[0][0]
                print(f"{Fore.YELLOW}[+] All sizes are the same! Applying filter Size: {size_filter} (-fs){Style.RESET_ALL}")
                self.run_ffuf_size(size_filter)
            elif second_field_repeats:
                word_filter = self.results[0][1]
                print(f"{Fore.YELLOW}[+] All word counts are the same! Applying filter Words: {word_filter} (-fw){Style.RESET_ALL}")
                self.run_ffuf_word(word_filter)
            elif third_field_repeats:
                line_filter = self.results[0][2]
                print(f"{Fore.YELLOW}[+] All line counts are the same! Applying filter Lines: {line_filter} (-fl){Style.RESET_ALL}")
                self.run_ffuf_line(line_filter)
            else:
                print(f"{Fore.RED}[!] Output variance detected! No repeating fields to filter on, skipping enumeration stage.{Style.RESET_ALL}")
                sys.exit()
        else:
            print(f"{Fore.YELLOW}[+] Only one result found, no need for filtering.{Style.RESET_ALL}")
            self.run_ffuf_real_no_filter()

    def process_ffuf_results(self, all_output):
        """
        Processes and categorizes FFUF results by status code, removes duplicates, 
        and prints them in a structured format with color-coding.
        """
        categorized_results = defaultdict(set)  # Using sets to remove duplicate lines

        # Process each FFUF output
        for output in all_output:  # Expecting all_output to be a list of raw outputs
            # Remove ANSI escape codes (colors)
            cleaned_output = self.strip_ansi_escape_codes(output)

            # Match full lines that contain FFUF results
            matches = re.findall(r"(.+\[Status:\s*\d{3}.*?\])", cleaned_output)

            for full_line in matches:
                # Extract status code from full line
                status_match = re.search(r"\[Status:\s*(\d{3})", full_line)
                if status_match:
                    status = int(status_match.group(1))  # Convert status code to an integer
                    if status == 403:
                        continue
                    categorized_results[status].add(full_line.strip())  # Store full line (removing duplicates)
                    

        # Print neatly formatted results
        print(f"{Fore.YELLOW}[+] Categorized FFUF Results:{Style.RESET_ALL}")

        for status_code in sorted(categorized_results.keys()):  # Sort by status code
            # Determine color based on status code group
            if 200 <= status_code < 300:
                color = Fore.GREEN  # 200s are Green
            elif 300 <= status_code < 400:
                color = Fore.BLUE   # 300s are Blue
            elif 400 <= status_code < 500:
                color = Fore.RED    # 400s are Red
            elif 500 <= status_code < 600:
                color = Fore.MAGENTA  # 500s are Magenta
            else:
                color = Fore.WHITE  # Default for any unexpected codes

            # Print status group with color
            print(f"\n{color}--- HTTP {status_code} Responses ---{Style.RESET_ALL}")

            # Print each full result line with correct color
            for full_line in sorted(categorized_results[status_code]):  # Sort for neatness
                print(f"{color}{full_line}{Style.RESET_ALL}")


    def strip_ansi_escape_codes(self, text):
        """Removes ANSI color codes from FFUF output."""
        return re.sub(r'\x1b\[[0-9;]*m', '', text)

    def run(self, wordlist):
        """
        Runs the entire ffuf automation process.
        """
        print(f"{Fore.BLUE} starting light directory enumration (dirsearch){Style.RESET_ALL}")
        self.run_dirsearch()
        #runs a small test to see if we are getting hits on the same thing repeativly it returns the output and saves it as output variable
        print(f"{Fore.BLUE}[-] starting enumrating directorys and files with FFUF{Style.RESET_ALL}")
        self.find_extension()
        output = self.run_ffuf_test(wordlist)
        #now we check if that list is empty if not we analyzne it
        if output:
            self.analyze_results(output)
        #skip to running no filter
        else:
            self.run_ffuf_real_no_filter()

