import re
from colorama import Fore, Style
from subdomainenumerator import SubdomainScanner
from subdomainenumerator import Passive_Subdomain_Finder
from cewl import WordlistGenerator
from directoryenumerator import DiectoryAutomation

class FfufAutomation:
    def __init__(self, url, cms=None, dev=False):
        """
        Initializes the ReconAutomation class with the target URL.
        """
        self.url = url
        self.is_ip = self.is_ip_address()  # Check if the URL is an IP
        self.cms = cms
        self.dev = dev

    def is_ip_address(self):
        """
        Checks if the provided URL contains an IP address.
        Returns True if it's an IP, otherwise False.
        """
        ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        host = self.url.replace("http://", "").replace("https://", "").strip("/")
        return bool(ip_pattern.match(host))

    def run_recon(self):
        """
        Runs the enumeration process based on whether the target is an IP or domain.
        """
        # Run CEWL wordlist generation
        cewler = WordlistGenerator(self.url, dev=self.dev)
        cewler.run_cewl()

        if self.is_ip:
            print(f"{Fore.RED}[!] The provided URL is an IP address. Skipping subdomain enumeration.{Style.RESET_ALL}")
        else:
            passive = Passive_Subdomain_Finder(self.url)
            passive.run()
            print(f"{Fore.GREEN}[+] Starting full enumeration for {self.url}{Style.RESET_ALL}")
            subdomain_enum = SubdomainScanner(self.url, dev=self.dev)
            subdomain_enum.sub_run()  # Run subdomain enumeration
        
        if self.cms:
            if "wordpress" in self.cms.lower():
                print(f"{Fore.CYAN}[+] Detected WordPress! Wordpress Enum coming soon! {Style.RESET_ALL}")    


        # Run directory enumeration with FFUF
        directory_enum = DiectoryAutomation(self.url, dev=self.dev)
        directory_enum.run("./De_Dup/rssfeed-files.txt")

# Example usage
if __name__ == "__main__":
    url = input(f"{Fore.YELLOW}[?] Enter the target URL: {Style.RESET_ALL}")
    recon = FfufAutomation(url, dev=True)
    recon.run_recon()
