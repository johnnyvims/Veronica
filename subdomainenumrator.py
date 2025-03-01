import os
import re
import subprocess
import sys
from colorama import Fore, Style

class SubdomainScanner:
    def __init__(self, url, dev=False):
        self.url = url
        self.results = []
        self.dev = dev

    def sub_run(self):
        output = self.run_sub_ffuf_test()
        if output:
            self.sub_analyze_results(output)
        else:
            print(f"{Fore.RED}[!]Big Bad Problem, no output from test! check your site carfully{Style.RESET_ALL}")


    def run_sub_ffuf_test(self):
        # Extract the hostname from the URL (remove "http://")
        host = self.url.replace("http://", "").replace("https://", "").strip("/")

        # Define the ffuf command
        ffuf_command = [
            "ffuf",
            "-w", "./Sub/test.txt:FUZZ",
            "-u", self.url,
            "-H", f"Host: FUZZ.{host}",
        ]
        try:
            print(f"{Fore.BLUE}[-]Running sub ffuf for target: {host}{Style.RESET_ALL}")
            
            
            # Run the ffuf command
            result = subprocess.run(ffuf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
           
            #debug
            print(f"{Fore.BLUE}checking output: \n {result.stdout.decode()}{Style.RESET_ALL}")

            return result.stdout.decode()
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running ffuf: {e}")


    def clean_output(self, output):
        """
        Clean the ffuf output to remove escape sequences like color codes.
        """
        clean = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', output)  # Remove escape sequences
        
        clean = self.clean_field(clean)

        return clean


    def clean_field(self, value):
        """
        Clean unwanted characters like `[` or `]` from specific fields.
        """
        # Remove unwanted characters like `[` or `]` from the output.
        #value = re.sub(r'[^\w\s,.-]', '', value).strip()
        #value = value.rstrip(', ')
        #print(value)

        value = re.sub(r'[^\w\s,.-]', '', value).strip()

        # Ensure no trailing commas or spaces
        value = re.sub(r'[\s,]+$', '', value)  

        return value


    def sub_analyze_results(self, output):
        """
        Analyzes the ffuf output and applies the filtering logic based on identical results.
        """
        cleaned_output = self.clean_output(output)  # Clean the output to remove color codes
        self.results = self.extract_ffuf_results(cleaned_output)
        

        #debug
        #self.results = self.extract_ffuf_results(output)
        #print(f"0 4: {self.results[0][4]} this should be size_fileter")
        #print(f"0 6: {self.results[0][6]} this should be word_filter")
        #print(f"0 8: {self.results[0][8]} this hsould be line_filter")

        #for result in self.results:
        #    print(result[4])
        #    print(f"for loop result {result}")


        if len(self.results) > 1:
            first_field_repeats = all(result[4] == self.results[0][4] for result in self.results)
            second_field_repeats = all(result[6] == self.results[0][6] for result in self.results)
            third_field_repeats = all(result[8] == self.results[0][8] for result in self.results)
            

            if first_field_repeats:
                size_filter = re.sub(r'[\s,]+$', '', self.results[0][4])
                print(f"{Fore.YELLOW}[+] All sizes are the same! Applying filter Size: {size_filter} (-fs){Style.RESET_ALL}")
                self.run_sub_size(size_filter)
            elif second_field_repeats:
                word_filter = re.sub(r'[\s,]+$', '', self.results[0][6])
                print(f"{Fore.YELLOW}[+] All word counts are the same! Applying filter Words: {word_filter} (-fw){Style.RESET_ALL}")
                self.run_sub_word(word_filter)
            elif third_field_repeats:
                line_filter = re.sub(r'[\s,]+$', '', self.results[0][8])
                print(f"{Fore.YELLOW}[+] All line counts are the same! Applying filter Lines: {line_filter} (-fl){Style.RESET_ALL}")
                self.run_sub_line(line_filter)
            else:
                print(f"{Fore.RED}[!] Output variance detected! No repeating fields to filter on, skipping enumeration stage.{Style.RESET_ALL}")
                sys.exit()
        else:
            print(f"{Fore.YELLOW}[+] Only one result found, no need for filtering.{Style.RESET_ALL}")
            self.run_ffuf_no_filter()


    def run_sub_size(self, size_filter):
        self.run_ffuf_with_filter("-fs", size_filter)


    def run_sub_word(self, word_filter):
        self.run_ffuf_with_filter("-fw", word_filter)


    def run_sub_line(self, line_filter):
        self.run_ffuf_with_filter("-fl", line_filter)


    def run_ffuf_with_filter(self, filter_option, filter_value):
        # Extract the hostname from the URL (remove "http://")
        host = self.url.replace("http://", "").replace("https://", "").strip("/")
        
        # Initialize the ffuf command
        ffuf_command = [
            "ffuf",
            "-u", self.url,
            "-H", f"Host: FUZZ.{host}",
            filter_option, filter_value,
            "-c"
        ]

        # Initialize an empty list for wordlists
        wordlists = []

        # Check if cewl.txt exists and add it to the list if it does
        if os.path.exists("cewl.txt"):
            wordlists.append("cewl.txt:FUZZ")
            print(f"{Fore.BLUE}[-] Found cewl.txt, adding it to the wordlist.{Style.RESET_ALL}")

        # Add the appropriate wordlist based on the dev flag
        if not self.dev:
            wordlists.append("./Sub/vhost_MEGA.txt:FUZZ")
            print(f"{Fore.BLUE}[-] Adding vhost_MEGA.txt to the wordlist.{Style.RESET_ALL}")
        else:
            wordlists.append("./Sub/quick_test.txt:FUZZ")
            print(f"{Fore.BLUE}[-] Adding quick_test.txt to the wordlist.{Style.RESET_ALL}")

        # Initialize output variable
        output = ""

        # Run ffuf for each wordlist in the wordlists list
        for wordlist in wordlists:
            # Add the current wordlist to the ffuf command
            ffuf_command.extend(["-w", wordlist])
    
            try:
                print(f"{Fore.BLUE}[-] Running ffuf for target: {host} using {wordlist}{Style.RESET_ALL}")
                result = subprocess.run(ffuf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                output += result.stdout.decode()  # Collect output
            except subprocess.CalledProcessError as e:
                print(f"An error occurred while running ffuf with {wordlist}: {e}")

        # Print combined output
        if output:
            print(f"{Fore.GREEN}[+] ffuf subdomain enumeration complete{Style.RESET_ALL}")
            print(output)
        else:
            print(f"{Fore.GREEN}[+] ffuf subdomain enumeration complete{Style.RESET_ALL}")
            print(f"{Fore.RED}[!] No results were found after running ffuf.{Style.RESET_ALL}")


    def extract_ffuf_results(self, output):
        """
        Parses the ffuf output and returns the extracted results.
        """
        # Implement your result extraction logic here
        # This is a placeholder for now
        return [line.split() for line in output.splitlines() if line]

    def run_ffuf_no_filter(self):
        # Run ffuf without filters, as per your logic in case of one result found.
        self.run_ffuf_with_filter("", "")

