#!/usr/bin/python3

import subprocess
import os
import sys
import threading
import re
import urllib.parse
import time
from termcolor import colored
from tqdm import tqdm

class CME_Enumration:
    def __init__(self, target):
        self.results = {}
        self.threads = []
        self.cms = ''
        self.cves = []
        self.target = target
        self.cms_regex_patterns = {
            'WordPress': re.compile(r'WordPress\s*(\d+\.\d+\.\d+)?', re.IGNORECASE),
            'Joomla': re.compile(r'Joomla\s*(\d+\.\d+)?', re.IGNORECASE),
            'Drupal': re.compile(r'Drupal\s*(\d+\.\d+)?', re.IGNORECASE),
            'Magento': re.compile(r'Magento\s*(\d+\.\d+)?', re.IGNORECASE),
            'Wix': re.compile(r'Wix', re.IGNORECASE),
            'Blogger': re.compile(r'Blogger', re.IGNORECASE),
            'Shopify': re.compile(r'Shopify', re.IGNORECASE),
            'Concrete5': re.compile(r'Concrete5', re.IGNORECASE),
            'Typo3': re.compile(r'Typo3', re.IGNORECASE),
            'PrestaShop': re.compile(r'PrestaShop', re.IGNORECASE),
            'XOOPS': re.compile(r'XOOPS', re.IGNORECASE),
            'ExpressionEngine': re.compile(r'ExpressionEngine', re.IGNORECASE),
            'SilverStripe': re.compile(r'SilverStripe', re.IGNORECASE),
            'Craft CMS': re.compile(r'Craft CMS', re.IGNORECASE),
            'Plone': re.compile(r'Plone', re.IGNORECASE),
            'OctoberCMS': re.compile(r'OctoberCMS', re.IGNORECASE),
            'Concrete CMS': re.compile(r'Concrete CMS', re.IGNORECASE),
            'Vbulletin': re.compile(r'vBulletin', re.IGNORECASE),
            'Zen Cart': re.compile(r'Zen Cart', re.IGNORECASE),
        }


    def banner(self):
        print(colored("""
        ==============================================
         RECON TOOL (Project: Verionica)
         Thorough Web Enumeration at Your Fingertips
        ==============================================
        """, "green"))



    # Function to check CMS presence
    def detect_cms(self, output, regex_dict):
        detected_cms = {}
    
        for cms, regex in regex_dict.items():
            match = regex.search(output)
            if match:
                detected_cms[cms] = match.group(0)
    
        return detected_cms

    def run_nikto(self):
        print(colored(f"\n[+] Running Nikto on {self.target}...", "blue"))
        nikto_command = ["nikto", "-h", self.target, "-C", "-Tuning", "b"]
    
        try:
            # Run nikto with subprocess and capture stdout
            process = subprocess.Popen(nikto_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Variables to track progress based on output
            total_output_lines = 0
            output_lines = []

            # While the process is running, print the progress based on output lines
            for line in process.stdout:
                total_output_lines += 1
                output_lines.append(line)
                if total_output_lines % 1 == 0:  # Update every 1 lines
                    print(colored(f"[+] Nikto has output {total_output_lines} lines...", "blue"))  # Print progress message

            # Get the output from Nikto
            stdout, stderr = process.communicate()

            final_output = "".join(output_lines) + stdout

            print(colored("[+] Nikto Finished.", "green"))
            self.results['nikto'] = final_output
            if stderr:
                print(colored(f"[!] Nikto errors: {stderr}", "red"))

        except FileNotFoundError:
            print(colored("[!] Nikto is not installed or not in PATH.", "red"))
        except Exception as e:
            print(colored(f"[!] An error occurred while running Nikto: {e}", "red"))


    def run_whatweb(self):
        print(colored(f"\n[+] Running WhatWeb on {self.target}...", "blue"))
        whatweb_command = ["whatweb", self.target]
        try:
            result = subprocess.run(whatweb_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(colored("[+] WhatWeb Finished.", "green"))
            self.results['whatweb'] = result.stdout
        except FileNotFoundError:
            print(colored("[!] WhatWeb is not installed or not in PATH.", "red"))
        except Exception as e:
            print(colored(f"[!] An error occurred while running WhatWeb: {e}", "red"))

    def run_wappalyzer(self):
        print(colored(f"\n[+] Running Wappalyzer CLI on {self.target}...", "blue"))
        wappalyzer_command = ["wappy", "-u", self.target]
        try:
            result = subprocess.run(wappalyzer_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(colored("[+] Wappalyzer Finished.", "green"))
            self.results['wappalyzer'] = result.stdout
        except FileNotFoundError:
            print(colored("[!] Wappalyzer CLI is not installed or not in PATH.", "red"))
        except Exception as e:
            print(colored(f"[!] An error occurred while running Wappalyzer: {e}", "red"))

    def save_results_to_file(self):
        try:
            with open(".cmsenumeration", "w") as file:
                for tool, output in self.results.items():
                    file.write(f"\n--- {tool.upper()} ---\n")
                    file.write(output + "\n")
            print(colored("[+] Results saved to .cmsenumeration", "yellow"))
        except Exception as e:
            print(colored(f"[!] An error occurred while saving results: {e}", "red"))

    def run_all(self):
        self.banner()
        target = self.target #we shouldnt need this when we can just call self.target
        
        cves = ''
        # Create threads for each task
        nikto_thread = threading.Thread(target=self.run_nikto, args=())
        whatweb_thread = threading.Thread(target=self.run_whatweb, args=())
        wappalyzer_thread = threading.Thread(target=self.run_wappalyzer, args=())

        # Add threads to list
        self.threads.extend([nikto_thread, whatweb_thread, wappalyzer_thread])

        # Start all threads
        for thread in self.threads:
            thread.start()

        # Join all threads
        for thread in self.threads:
            thread.join()

        print(colored("\n[+] All tasks completed. Aggregated Results:", "yellow"))
        
        #here we loop throught the dictionary of self.results.items() which contains the tools which are "niko, whatsweb, wapanalizer" and the results of the tool output
        for tool, output in self.results.items():
            print(colored(f"\n--- {tool.upper()} ---\n", "cyan"))
            print(colored(output, "green"))
            cves = re.findall(r'CVE-\d{4}-\d{4,}', output)
            interfaces = re.findall(r'\/[^\s]+:.*?interface found', output, re.IGNORECASE)
            if tool =="wappalyzer" and self.cms == '':
                print(colored("Checking for CMS in wappalyzer output...", "blue"))
                cms_match = re.search(r'CMS : (.+?) \[version: (.+?)\]', output)
                if cms_match:
                    cms = cms_match.group(1)
                    cms_version = cms_match.group(2)
                    if cms_version.lower() == "nil":
                        self.cms = cms
                    else:
                        self.cms = f"{cms} {cms_version}"
                    print(colored(f"Detected CMS from Wappalyzer: {self.cms}", "green"))
                else:
                    cms_match = self.detect_cms(output, self.cms_regex_patterns)
                    if cms_match:
                        key_list = list(cms_match.keys())
                        #print(f"key list: {key_list}")
                        self.cms = key_list[0]


            elif tool == "whatweb" and self.cms == '': #change to correct tool name
                print(colored("Checking for CMS in WhatWeb output...", "blue"))
   
                ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
                clean_output = ansi_escape.sub('', output)  # Strip ANSI codes

                cms_match = re.search(r"(WordPress|Joomla|Drupal|Magento|Wix|Blogger|Shopify|Concrete5|Typo3|PrestaShop|XOOPS|ExpressionEngine|SilverStripe|Plone|OctoberCMS|Vbulletin)\[(\d+\.\d+\.\d+)\]", clean_output, re.IGNORECASE,)
                
                if cms_match:
                    cms_name = cms_match.group(1)
                    cms_version = cms_match.group(2)
                    self.cms = f"{cms_name} {cms_version}"
                    print(colored(f"Detected CMS from WhatWeb: {self.cms}", "red"))


            elif tool == "nikto" and self.cms == '':
                print(colored("Checking for CMS in Nikto output...", "blue"))
                cms_match = re.search(r'Appears to be a default (.+?) install', output, re.IGNORECASE)
                if cms_match:
                    cms = cms_match.group(1)
                    self.cms = cms
                    print(colored(f"Detected CMS from Nikto: {self.cms}", "red"))
                else:
                    cms_match = re.search(r'([A-Za-z0-9]+(?:\s?[A-Za-z0-9]+)?)\s*(?:\d+)\s*(?:was|is)\s*identified\s*(?:via|with)\s*the\s*(?:x-generator)\s*header\.', output, re.IGNORECASE)
                    if cms_match:
                        cms = cms_match.group(1)
                        self.cms = cms
                    else:
                        cms_match = self.detect_cms(output, self.cms_regex_patterns)
                        if cms_match:
                            key_list = list(cms_match.keys())
                            #key_list = list(cms_match.items())
                            print(f"key list: {key_list}")
                            self.cms = key_list[0]

            if tool == "nikto":
                #file_matches = re.findall(r'(/[\w\-\.]+(?:\.php|\.txt|\.xml)?)\s*(?:found|identified)', output, re.IGNORECASE)
                intresting_matches = re.findall(r'\+\s(/[\w\-/]+/?):\s.*?interesting\.', output, re.IGNORECASE)
                file_matches = re.findall(r'\+\s(/[\w\-/\.]+):\s.*?(file\sfound|accessible)\.', output, re.IGNORECASE)
                if file_matches:
                    file_matches = list(dict.fromkeys(file_matches))
                    print(colored(f'you might wanna check these', 'yellow'))
                    for file in file_matches:
                        print(colored(f"Found file: {file}", "yellow"))
                if intresting_matches:
                    intresting_matches = list(dict.fromkeys(intresting_matches))
                    for file in intresting_matches:
                        print(colored(f"intresting file {file}", "yellow"))
                
        if not self.cms:
            self.cms = "Unknown"
            print(colored("No CMS detected from tools.", "red"))

        # Print detected information
        print(colored(f"Found CMS: {self.cms}", "white", "on_green"))
        if cves:
            print(colored(f"Extracted CVEs: {cves}", "white", "on_green"))
        print("\n")

        # Fetch online CVEs
        if self.cms != "Unknown":
            #search search sploit
            searchsploit = subprocess.run(["searchsploit", f"{self.cms}"],text=True,capture_output=True)

            if searchsploit.returncode != 0:
                print("Error running searchsploit:")

            searchsploit_output = searchsploit.stdout

            print(colored(searchsploit_output, "green"))

            unauth_exploits = []
            print(colored("[+]checking for unauth exploits (quick wins)", "blue"))
            for line in searchsploit_output.splitlines():
                if re.search(r'unauthenticated', line, re.IGNORECASE):
                    unauth_exploits.append(line)
            if unauth_exploits:
                unauth_exploits = list(dict.fromkeys(unauth_exploits))
                for line in unauth_exploits:
                    print(colored(line, "green"))
            else:
                print(colored("[-]sorry no quick wins, check the full output above, you will have do some work", "yellow"))


            print(colored(f"\nChecking online for newest CVEs for {self.cms}\n", "blue"))
            encoded_cms = urllib.parse.quote(self.cms)
            curl_command = ["curl", f"https://www.tenable.com/cve/search?q={encoded_cms}&sort=newest&page=1"]

            online_cves = []  # Initialize online_cves
            try:
                check_for_cves = subprocess.run(curl_command, text=True, capture_output=True, check=True).stdout
                online_cves = re.findall(r'CVE-\d{4}-\d{4,}', check_for_cves)
            except subprocess.CalledProcessError as e:
                print(colored(f"Error fetching CVEs: {e}", "red"))

            # Display online CVEs
            if online_cves:
                print(colored("-----------------------------------------------------", "yellow"))
                print(colored(f"Current CVEs online: {online_cves}", "green"))
                print(colored("-----------------------------------------------------", "yellow"))
            else:
                print(colored("No CVEs found online for the detected CMS.", "yellow"))

        

        self.save_results_to_file()

